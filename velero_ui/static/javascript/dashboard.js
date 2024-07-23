
function parseBackupData(data) {
  const backupList = [];

  function parseBackup(backup) {
    const {
      metadata: { name, creationTimestamp },
      status: { phase, expiration, errors = 0, warnings = 0 },
      spec: { storageLocation },
    } = backup;

    return {
      name,
      status: phase || 'New',
      errors,
      warnings,
      created: creationTimestamp || '<nil>',
      expiration: expiration || 'n/a',
      storageLocation: storageLocation || '<none>',
      selector: '<none>',
    };
  }

  if (data) {
    if (data.items) {
      backupList.push(...data.items.filter(item => item.metadata).map(parseBackup));
    } else if (data.metadata) {
      backupList.push(parseBackup(data));
    }
  }

  return backupList;
}

function parseScheduleData(data) {
  const scheduleList = [];

  if (data.kind === "ScheduleList" && data.items) {
    data.items.forEach((item) => {
      const scheduleData = extractScheduleData(item);
      if (scheduleData) {
        scheduleList.push(scheduleData);
      }
    });
  } else if (data.kind === "Schedule") {
    const scheduleData = extractScheduleData(data);
    if (scheduleData) {
      scheduleList.push(scheduleData);
    }
  }

  return scheduleList;
}

function parseStorageData(data) {
  const storageList = [];

  function parseStorage(storage) {
    const {
      metadata: { name, creationTimestamp },
      status: { phase, lastValidationTime },
      spec: { backupSyncPeriod, config },
    } = storage;

    return {
      name,
      status: phase || 'New',
      lastValidationTime: lastValidationTime,
      created: creationTimestamp || '<nil>',
      backupSyncPeriod,
      config
    };
  }

  if (data) {
    if (data.items) {
      storageList.push(...data.items.filter(item => item.metadata).map(parseStorage));
    } else if (data.metadata) {
      storageList.push(parseStorage(data));
    }
  }

  return storageList;
}

function extractScheduleData(item) {
  if (item.metadata && item.spec && item.status) {
    const {
      metadata: { name, creationTimestamp },
      spec: { schedule, template: { ttl } },
      status: { phase },
    } = item;

    return {
      name,
      status: phase,
      created: creationTimestamp,
      schedule,
      backupTtl: ttl,
      lastBackup: "n/a", // You need to update this value based on your API response
      selector: "<none>",
      paused: false, // You need to update this value based on your API response
    };
  }
  return null;
}

async function loadDashboardSummary() {
  const backupResponse = await fetch(`backups`);
  const backupData = await backupResponse.json();
  const backupList = parseBackupData(JSON.parse(backupData));


  const scheduleResponse = await fetch(`schedules`);
  const scheduleData = await scheduleResponse.json();
  const scheduleList = parseScheduleData(JSON.parse(scheduleData));

  const storageReponse = await fetch(`storages`);
  const storageData = await storageReponse.json();
  const storageList = parseStorageData(JSON.parse(storageData));

  displayDashboardSummary(backupList, scheduleList, storageList);
}

function displayDashboardSummary(backupList, scheduleList, storageList) {
  const totalBackups = backupList.length;
  const totalSchedules = scheduleList.length;

  const backupsByStatus = backupList.reduce((statusCounts, backup) => {
    if (statusCounts[backup.status]) {
      statusCounts[backup.status]++;
    } else {
      statusCounts[backup.status] = 1;
    }
    return statusCounts;
  }, {});

  document.getElementById("totalBackups").innerText = `Total Backups: ${totalBackups}`;
  document.getElementById("totalSchedules").innerText = `Total Schedules: ${totalSchedules}`;

  const storageTable = document.getElementById("storageLocation")
  const table = document.createElement('tbody')

  const keys = ["name", "config", "status", "lastValidationTime"]

  for (let storage in storageList) {
    let row = document.createElement('tr');
  
    keys.forEach(function(key) {
      let cell = document.createElement('td');
      let cellText = document.createTextNode(JSON.stringify(storageList[storage][key], null, 2).replace(/"/g, ""));
      
      cell.appendChild(cellText);
      row.appendChild(cell);
    })

    if (storageList[storage]["status"] == "Available") {
      row.classList.add("bg-success")
    } else {
      row.classList.add("bg-danger")
    }
      

    table.appendChild(row)
  }

  storageTable.appendChild(table)

  let backupsByStatusText = "Backups by Status:";
  for (const [status, count] of Object.entries(backupsByStatus)) {
    backupsByStatusText += `\n- ${status}: ${count}`;
  }
  document.getElementById("backupsByStatus").innerText = backupsByStatusText;
}

document.addEventListener("DOMContentLoaded", loadDashboardSummary);

