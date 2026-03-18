'use strict';

exports = {
  onAppInstallHandler: async function (args) {
    let freq = parseInt(args.iparams.sync_interval_minutes, 10);
    if (isNaN(freq) || freq < 5) {
      freq = 30;
    }
    try {
      await $schedule.create({
        name: 'jira_helpdesk_sync',
        data: {},
        schedule_at: new Date(Date.now() + 60000).toISOString(),
        repeat: { time_unit: 'minutes', frequency: freq }
      });
    } catch {
      console.error('APP006 schedule create error');
    }
  },

  onAppUninstallHandler: async function () {
    try {
      await $schedule.delete({ name: 'jira_helpdesk_sync' });
    } catch {
      console.error('APP006 schedule delete error');
    }
  },

  onScheduledEventHandler: async function (args) {
    await runScheduledSync(args);
  },

  onTicketCreateHandler: async function (args) {
    await handleFreshdeskTicketCreate(args);
  },

  onTicketUpdateHandler: async function (args) {
    await handleFreshdeskTicketUpdate(args);
  }
};

function safeJsonParse(str, fallback) {
  try {
    return str ? JSON.parse(str) : fallback;
  } catch {
    return fallback;
  }
}

function jiraDescriptionToText(desc) {
  if (typeof desc === 'string') {
    return desc;
  }
  if (desc && typeof desc === 'object') {
    return JSON.stringify(desc).substring(0, 8000);
  }
  return '';
}

function mapJiraStatusToHelpdesk(statusName, mapping) {
  if (!mapping || !statusName) {
    return null;
  }
  const mapped = mapping[statusName];
  return mapped ? parseInt(mapped, 10) : null;
}

async function getStoredTicketId(dbKey) {
  try {
    const existing = await $db.get(dbKey);
    return existing && existing.ticket_id ? existing.ticket_id : null;
  } catch {
    return null;
  }
}

async function helpdeskUpdateTicket(ticketId, updatePayload) {
  try {
    await $request.invokeTemplate('helpdeskUpdateTicket', {
      context: { ticketId: String(ticketId) },
      body: JSON.stringify(updatePayload)
    });
  } catch {
    console.error('APP006 helpdesk update failed');
  }
}

async function helpdeskCreateAndStore(dbKey, createPayload) {
  let resp;
  try {
    resp = await $request.invokeTemplate('helpdeskCreateTicket', {
      context: {},
      body: JSON.stringify(createPayload)
    });
  } catch {
    console.error('APP006 helpdesk create failed');
    return;
  }
  let body = resp.response;
  if (typeof body === 'string') {
    body = JSON.parse(body);
  }
  if (body.id) {
    await $db.set(dbKey, { ticket_id: body.id });
  }
}

function buildJiraToHelpdeskContext(issue, iparams) {
  const key = issue.key;
  const fields = issue.fields || {};
  const summary = fields.summary || key;
  const statusMap = safeJsonParse(iparams.status_mapping_json, {});
  const jiraStatus = fields.status && fields.status.name;
  const statusId = mapJiraStatusToHelpdesk(jiraStatus, statusMap);
  const dbKey = 'jira_fd_' + key;
  const desc = 'Synced from Jira ' + key + '\n\n' + jiraDescriptionToText(fields.description);
  const gid = iparams.freshdesk_group_id ? parseInt(iparams.freshdesk_group_id, 10) : 0;
  return {
    dbKey: dbKey,
    summary: summary,
    desc: desc,
    statusId: statusId,
    email: iparams.sync_requester_email,
    gid: gid
  };
}

function buildUpdatePayloadFromJira(ctx) {
  const updatePayload = { description: ctx.desc.substring(0, 65535) };
  if (ctx.statusId) {
    updatePayload.status = ctx.statusId;
  }
  return updatePayload;
}

function buildCreatePayloadFromJira(ctx) {
  const createPayload = {
    email: ctx.email,
    subject: ctx.summary.substring(0, 255),
    description: ctx.desc.substring(0, 65535),
    priority: 2,
    status: ctx.statusId || 2
  };
  if (ctx.gid > 0) {
    createPayload.group_id = ctx.gid;
  }
  return createPayload;
}

async function syncOneIssue(issue, iparams) {
  const ctx = buildJiraToHelpdeskContext(issue, iparams);
  const ticketId = await getStoredTicketId(ctx.dbKey);
  if (ticketId) {
    await helpdeskUpdateTicket(ticketId, buildUpdatePayloadFromJira(ctx));
    return;
  }
  await helpdeskCreateAndStore(ctx.dbKey, buildCreatePayloadFromJira(ctx));
}

async function fetchJiraIssueList(iparams) {
  const jql = 'project=' + iparams.jira_project_key + ' ORDER BY updated DESC';
  const searchResp = await $request.invokeTemplate('jiraSearchPost', {
    context: {},
    body: JSON.stringify({
      jql: jql,
      maxResults: 15,
      fields: ['summary', 'status', 'description']
    })
  });
  let raw = searchResp.response;
  if (typeof raw === 'string') {
    raw = JSON.parse(raw);
  }
  return raw.issues || [];
}

async function runScheduledSync(args) {
  const iparams = args.iparams || {};
  const ready = iparams.jira_cloud_id && iparams.helpdesk_basic_auth && iparams.jira_project_key;
  if (!ready) {
    console.info('APP006 sync skipped');
    return;
  }
  let issues;
  try {
    issues = await fetchJiraIssueList(iparams);
  } catch {
    console.error('APP006 jira search failed');
    return;
  }
  let i = 0;
  while (i < issues.length) {
    await syncOneIssue(issues[i], iparams);
    i += 1;
  }
}

function buildJiraIssuePayload(ticket, iparams) {
  const typeName = (iparams.jira_issue_type || 'Task').trim();
  return {
    fields: {
      project: { key: iparams.jira_project_key },
      summary: (ticket.subject || 'Ticket').substring(0, 255),
      issuetype: { name: typeName },
      description: {
        type: 'doc',
        version: 1,
        content: [
          {
            type: 'paragraph',
            content: [{ type: 'text', text: 'From Freshdesk #' + ticket.id }]
          }
        ]
      }
    }
  };
}

function canSyncTicketToJira(ticket, iparams) {
  return Boolean(
    ticket && ticket.subject && iparams.jira_cloud_id && iparams.jira_project_key
  );
}

async function invokeJiraCreateAndLink(ticket, iparams) {
  const body = buildJiraIssuePayload(ticket, iparams);
  let resp;
  try {
    resp = await $request.invokeTemplate('jiraCreateIssue', {
      context: {},
      body: JSON.stringify(body)
    });
  } catch {
    console.error('APP006 jira create failed');
    return;
  }
  let jr = resp.response;
  if (typeof jr === 'string') {
    jr = JSON.parse(jr);
  }
  if (jr.key) {
    await $db.set('fd_jira_' + ticket.id, { jira_key: jr.key });
  }
}

async function handleFreshdeskTicketCreate(args) {
  const ticket = args.data && args.data.ticket;
  const iparams = args.iparams || {};
  if (!canSyncTicketToJira(ticket, iparams)) {
    return;
  }
  await invokeJiraCreateAndLink(ticket, iparams);
}

async function loadJiraKeyForTicket(ticketId) {
  try {
    const rec = await $db.get('fd_jira_' + ticketId);
    return rec && rec.jira_key ? rec.jira_key : null;
  } catch {
    return null;
  }
}

async function postJiraUpdateComment(issueKey, ticketId) {
  const comment = {
    body: {
      type: 'doc',
      version: 1,
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Freshdesk ticket #' + ticketId + ' was updated.' }]
        }
      ]
    }
  };
  try {
    await $request.invokeTemplate('jiraAddComment', {
      context: { issueKey: issueKey },
      body: JSON.stringify(comment)
    });
  } catch {
    console.error('APP006 jira comment failed');
  }
}

async function handleFreshdeskTicketUpdate(args) {
  const ticket = args.data && args.data.ticket;
  const iparams = args.iparams || {};
  if (!ticket || !ticket.id || !iparams.jira_cloud_id) {
    return;
  }
  const jiraKey = await loadJiraKeyForTicket(ticket.id);
  if (!jiraKey) {
    return;
  }
  await postJiraUpdateComment(jiraKey, ticket.id);
}
