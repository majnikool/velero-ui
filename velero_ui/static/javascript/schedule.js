import { createButton, displayDataInModal, hideSpinnerAndShowData } from "./utils.js";

let submitCreateScheduleInitialized = false;

function initSchedulePage() {
  listSchedules();


  if (!submitCreateScheduleInitialized) {
    const createScheduleForm = document.getElementById("createScheduleForm");
    const createScheduleButton = document.getElementById("submitCreateSchedule");
    
    createScheduleButton.addEventListener("click", () => {
      createSchedule();
      createScheduleForm.reset();
      $("#createScheduleModal").modal("hide");
    });
    submitCreateScheduleInitialized = true;
  }

  const deleteScheduleForm = document.getElementById("deleteScheduleForm");
  const submitDeleteSchedule = document.getElementById("submitDeleteSchedule");

  submitDeleteSchedule.addEventListener("click", () => {
    deleteSchedule(deleteScheduleForm.deleteScheduleName.value);
    deleteScheduleForm.reset();
    $("#deleteScheduleModal").modal("hide");
  });
}

async function restoreSchedule(scheduleName, optionalParameters) {
  const response = await fetch('restores', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      scheduleName: scheduleName,
      optionalParameters: optionalParameters,
    }),
  });

  const data = await response.json();
  alert(data.message);
}

$(document).ready(initSchedulePage);

function displayScheduleData(scheduleData) {
  const tableBody = document.querySelector("#schedulesTableBody");
  tableBody.innerHTML = "";

  scheduleData.forEach((schedule) => {
    const newRow = tableBody.insertRow();

    newRow.insertCell().innerText = schedule.name;
    newRow.insertCell().innerText = schedule.status;
    newRow.insertCell().innerText = new Date(schedule.created).toLocaleString();
    newRow.insertCell().innerText = schedule.schedule;
    newRow.insertCell().innerText = schedule.backupTtl;
    newRow.insertCell().innerText = schedule.lastBackup;
    newRow.insertCell().innerText = schedule.selector;
    newRow.insertCell().innerText = schedule.paused;

    const actionsCell = newRow.insertCell();
    const deleteButton = createButton("Delete", () => {
      const confirmation = confirm(`Are you sure you want to delete schedule "${schedule.name}"?`);
      if (confirmation) {
        deleteSchedule(schedule.name);
      }
    });
    actionsCell.appendChild(deleteButton);
    const describeButton = createButton("Describe", () => {
      displayDataInModal(null, "scheduleDescribeModal", async () => {
        try {
        const response = await fetch(`schedules/describe?name=${schedule.name}`);
          if (!response.ok) {
            throw new Error(`${response.status} ${response.statusText}`);
          }
          const data = await response.json();
          if (data.message) {
            alert(data.message);
          } else {
            displayDataInModal(data, "scheduleDescribeModal");
          }
        } catch (error) {
          console.error("Error fetching schedule describe:", error);
          alert(`Error fetching schedule describe: ${error.message}`);
        } finally {
          hideSpinnerAndShowData("scheduleDescribeModal");
        }
      });
      $("#scheduleDescribeModal").modal("show");
    });
    actionsCell.appendChild(describeButton);
  });

  // Add the event listener for the dismiss buttons once, outside the loop
  const dismissButtons = document.querySelectorAll(".modal-header button");
  for (const dismissButton of dismissButtons) {
    dismissButton.addEventListener("click", () => {
      console.log("Dismiss button clicked");
      $(dismissButton.closest(".modal")).modal("hide");
    });
  }
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

function extractScheduleData(item) {
  if (item.metadata && item.spec && item.status) {
    const {
      metadata: { name, creationTimestamp },
      spec: { schedule, template: { ttl, labelSelector } },
      status: { phase, lastBackup },
    } = item;

    return {
      name,
      status: phase,
      created: creationTimestamp,
      schedule,
      backupTtl: ttl,
      lastBackup: lastBackup ? new Date(lastBackup).toLocaleString() : "n/a",
      selector: JSON.stringify(labelSelector, null, 2) || "<none>",
      paused: false,
    };
  }
  return null;
}

async function listSchedules() {
  const response = await fetch(`schedules`);
  const data = await response.json();
  const scheduleList = parseScheduleData(JSON.parse(data));
  displayScheduleData(scheduleList);
}

async function createSchedule() {
  const createScheduleForm = document.getElementById("createScheduleForm");

  const metadata_name = createScheduleForm.metadata_name.value;
  const spec_includedNamespaces = createScheduleForm.spec_includedNamespaces.value;
  const spec_ttl = createScheduleForm.spec_ttl.value;
  const spec_schedule = createScheduleForm.spec_schedule.value;
  const spec_labels = createScheduleForm.spec_labels.value;


  if (!metadata_name || !spec_includedNamespaces || !spec_ttl || !spec_schedule) {
    alert("ERROR: Input fields cannot be empty")
    return
  }

  const splited_spec_includedNamespaces = spec_includedNamespaces.split(',')

  if (splited_spec_includedNamespaces.length < 0) {
    alert("ERROR: No namespace found. Must be comman-separated");
    return
  }

  const splited_spec_labels = spec_labels.split(',');

  try {
    const response = await fetch("schedules", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        metadata_name: metadata_name,
        spec_includedNamespaces: splited_spec_includedNamespaces,
        spec_ttl: spec_ttl,
        spec_schedule: spec_schedule,
        spec_labels: splited_spec_labels
      }),
    });

    if (response.ok) {
      const result = await response.json();
      alert(result.message);
      listSchedules();
    } else {
      const error = await response.json();
      alert(error.message);
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while creating the schedule.");
  }
}

async function deleteSchedule(scheduleName) {
  if (!scheduleName) return;

  const response = await fetch(`schedules?name=${scheduleName}`, {
    method: "DELETE",
  });
  const data = await response.json();
  alert(data.message);
  listSchedules();
}

window.parseScheduleData = window.parseScheduleData || parseScheduleData;
