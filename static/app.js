const stateUrl = "/api/state";
const startQuestUrl = "/api/start-quest";
const loadTestFileUrl = "/api/load-test-file";
const equipItemUrl = "/api/equip-item";

let selectedCharacterKey = "";
let selectedInventoryCharacterKey = "";

function formatSeconds(seconds) {
  return `${Math.floor(seconds)}s`;
}

function renderCharacters(characters) {
  const list = document.querySelector("#character-list");
  if (!list) {
    return;
  }

  list.innerHTML = "";

  for (const character of characters) {
    const row = document.createElement("article");
    row.className = "row";
    row.innerHTML = `
      <div class="row-title">
        <strong>${character.name}</strong>
        <span class="muted">
          ${character.job} Lv.${character.level}${character.busy ? " - Questing" : ""}
        </span>
      </div>
      <div class="stats">
        <div class="stat"><span>STR</span><strong>${character.strength}</strong></div>
        <div class="stat"><span>INT</span><strong>${character.intelligence}</strong></div>
        <div class="stat"><span>AGI</span><strong>${character.agility}</strong></div>
        <div class="stat"><span>WIS</span><strong>${character.wisdom}</strong></div>
        <div class="stat"><span>EXP</span><strong>${character.experience}</strong></div>
      </div>
    `;
    list.appendChild(row);
  }
}

function renderCharacterSelect(characters) {
  const select = document.querySelector("#character-select");
  if (!select) {
    return;
  }

  const previousValue = selectedCharacterKey;
  const availableCharacters = characters.filter((character) => !character.busy);

  select.innerHTML = "";

  if (availableCharacters.length === 0) {
    const option = document.createElement("option");
    option.textContent = "No available members";
    option.value = "";
    select.appendChild(option);
    select.disabled = true;
    selectedCharacterKey = "";
    return;
  }

  select.disabled = false;

  for (const character of availableCharacters) {
    const option = document.createElement("option");
    option.value = character.key;
    option.textContent = `${character.name} (${character.job})`;

    if (character.key === previousValue) {
      option.selected = true;
    }

    select.appendChild(option);
  }

  if (!availableCharacters.some((character) => character.key === selectedCharacterKey)) {
    selectedCharacterKey = availableCharacters[0].key;
    select.value = selectedCharacterKey;
  }

  select.onchange = () => {
    selectedCharacterKey = select.value;
  };
}

function renderQuests(quests) {
  const list = document.querySelector("#quest-list");
  if (!list) {
    return;
  }

  const hasSelectedCharacter = selectedCharacterKey !== "";
  list.innerHTML = "";

  for (const quest of quests) {
    const row = document.createElement("article");
    row.className = "quest";
    row.innerHTML = `
      <div class="row-title">
        <strong>${quest.name}</strong>
        <span class="muted">${quest.time_to_complete_seconds}s</span>
      </div>
      <p class="muted">${quest.check_count} checks</p>
      <button type="button" data-quest-key="${quest.key}" ${hasSelectedCharacter ? "" : "disabled"}>
        Start Quest
      </button>
    `;

    row.querySelector("button").onclick = () => {
      startQuest(quest.key);
    };

    list.appendChild(row);
  }
}

function renderActiveQuests(activeQuests) {
  const list = document.querySelector("#active-quest-list");
  if (!list) {
    return;
  }

  list.innerHTML = "";

  if (activeQuests.length === 0) {
    list.innerHTML = `<p class="muted">No active quests.</p>`;
    return;
  }

  for (const quest of activeQuests) {
    const row = document.createElement("article");
    row.className = "active-quest";

    const checks = quest.checks.map((check) => {
      let className = "check";
      let status = "Pending";

      if (check.complete && check.passed) {
        className += " done";
        status = "Passed";
      } else if (check.complete) {
        className += " failed";
        status = "Failed";
      }

      return `
        <div class="${className}">
          <span>${check.description}</span>
          <strong>${status}</strong>
        </div>
      `;
    }).join("");

    row.innerHTML = `
      <div class="row-title">
        <strong>${quest.character_name} - ${quest.quest_name}</strong>
        <span class="muted">
          ${formatSeconds(quest.time_elapsed_seconds)} / ${formatSeconds(quest.time_to_complete_seconds)}
        </span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${quest.progress_percent}%"></div>
      </div>
      <div class="checks">${checks}</div>
    `;
    list.appendChild(row);
  }
}

function renderInventory(inventory, characters = []) {
  const list = document.querySelector("#inventory-list");
  if (!list) {
    return;
  }

  const selectedCharacter = characters.find(
    (character) => character.key === selectedInventoryCharacterKey
  );

  list.innerHTML = "";

  if (inventory.length === 0) {
    list.innerHTML = `<p class="muted">Inventory is empty.</p>`;
    return;
  }

  const sortedInventory = sortInventoryForCharacter(inventory, selectedCharacter);
  const inventoryGroups = groupItemsBySlot(sortedInventory);

  for (const [slot, items] of inventoryGroups) {
    const group = document.createElement("section");
    group.className = "inventory-group";
    group.innerHTML = `<h3>${formatSlotName(slot)}</h3>`;

    const groupList = document.createElement("div");
    groupList.className = "stack compact";

    for (const item of items) {
      groupList.appendChild(renderInventoryItem(item, selectedCharacter));
    }

    group.appendChild(groupList);
    list.appendChild(group);
  }
}

function renderInventoryItem(item, selectedCharacter) {
  const equipCheck = getEquipCheck(selectedCharacter, item);
  const equippedItem = getEquippedItemForSlot(selectedCharacter, item.slot);
  const statDeltas = getItemDeltas(item, equippedItem);
  const row = document.createElement("div");
  row.className = `item rarity-${cssClassToken(item.rarity)}`;
  row.innerHTML = `
      <div class="row-title">
        <strong>${item.name}</strong>
        <span class="rarity-pill">${item.rarity}</span>
      </div>
      <div class="item-summary">
        <span>${item.slot}</span>
        <span>${renderEquippedComparison(equippedItem, selectedCharacter, item)}</span>
      </div>
      <div class="item-deltas">
        ${renderItemDeltas(statDeltas)}
      </div>
      ${equipCheck.reason ? `<p class="equip-reason">${equipCheck.reason}</p>` : ""}
      <details class="item-details">
        <summary>Details</summary>
        <div class="item-requirements">
          <span>Level ${item.level_requirement}</span>
          <span>Job: ${formatJobRestriction(item.job_restriction)}</span>
          ${item.hands ? `<span>${item.hands}H</span>` : ""}
        </div>
        <div class="item-bonuses">
          ${renderItemBonus("STR", item.strength_bonus)}
          ${renderItemBonus("INT", item.intelligence_bonus)}
          ${renderItemBonus("AGI", item.agility_bonus)}
          ${renderItemBonus("WIS", item.wisdom_bonus)}
          ${renderItemBonus("HP", item.health_bonus)}
          ${renderItemBonus("MP", item.mana_bonus)}
        </div>
        ${item.flavor_text ? `<p class="muted">${item.flavor_text}</p>` : ""}
        <div class="item-meta">
          <span>${item.instance_id}</span>
          <span>${item.template_id}</span>
        </div>
      </details>
      <button
        class="command-button"
        type="button"
        data-instance-id="${item.instance_id}"
        ${equipCheck.canEquip ? "" : "disabled"}
      >
        ${equipCheck.label}
      </button>
    `;
  row.querySelector("button").onclick = () => {
    equipItem(item.instance_id);
  };

  return row;
}

function sortInventoryForCharacter(inventory, character) {
  return [...inventory].sort((firstItem, secondItem) => {
    const firstCheck = getEquipCheck(character, firstItem);
    const secondCheck = getEquipCheck(character, secondItem);

    if (firstCheck.canEquip !== secondCheck.canEquip) {
      return firstCheck.canEquip ? -1 : 1;
    }

    return firstItem.slot.localeCompare(secondItem.slot)
      || firstItem.name.localeCompare(secondItem.name)
      || firstItem.instance_id.localeCompare(secondItem.instance_id);
  });
}

function groupItemsBySlot(items) {
  const groups = new Map();

  for (const item of items) {
    if (!groups.has(item.slot)) {
      groups.set(item.slot, []);
    }

    groups.get(item.slot).push(item);
  }

  return groups;
}

function getEquippedItemForSlot(character, slot) {
  if (!character || !character.equipment) {
    return null;
  }

  return character.equipment[slot] || null;
}

function getItemStatMap(item) {
  return {
    STR: item?.strength_bonus || 0,
    INT: item?.intelligence_bonus || 0,
    AGI: item?.agility_bonus || 0,
    WIS: item?.wisdom_bonus || 0,
    HP: item?.health_bonus || 0,
    MP: item?.mana_bonus || 0
  };
}

function getItemDeltas(item, equippedItem) {
  const nextStats = getItemStatMap(item);
  const currentStats = getItemStatMap(equippedItem);

  return Object.entries(nextStats)
    .map(([label, value]) => ({
      label,
      delta: value - currentStats[label]
    }))
    .filter((stat) => stat.delta !== 0);
}

function renderEquippedComparison(equippedItem, selectedCharacter, item) {
  if (!selectedCharacter) {
    return "Select a member to compare";
  }

  if (!Object.prototype.hasOwnProperty.call(selectedCharacter.equipment, item.slot)) {
    return "No matching equipment slot";
  }

  return `vs ${equippedItem ? equippedItem.name : "Empty"}`;
}

function renderItemDeltas(deltas) {
  if (deltas.length === 0) {
    return `<span class="muted">No stat change</span>`;
  }

  return deltas.map(({ label, delta }) => {
    const className = delta > 0 ? "delta-positive" : "delta-negative";
    const sign = delta > 0 ? "+" : "";

    return `<span class="${className}">${label} ${sign}${delta}</span>`;
  }).join("");
}

function getEquipCheck(character, item) {
  if (!character) {
    return {
      canEquip: false,
      label: "Select Member",
      reason: "Choose a guild member to see equip options."
    };
  }

  if (character.busy) {
    return {
      canEquip: false,
      label: "Questing",
      reason: `${character.name} cannot change equipment while questing.`
    };
  }

  if (!Object.prototype.hasOwnProperty.call(character.equipment, item.slot)) {
    return {
      canEquip: false,
      label: "Invalid Slot",
      reason: `${item.slot} is not an equipment slot for ${character.name}.`
    };
  }

  if (character.level < item.level_requirement) {
    return {
      canEquip: false,
      label: `Requires Lv.${item.level_requirement}`,
      reason: `${character.name} is level ${character.level}.`
    };
  }

  if (!jobMatches(character.job, item.job_restriction)) {
    return {
      canEquip: false,
      label: `Requires ${item.job_restriction}`,
      reason: `${character.name} is a ${character.job}.`
    };
  }

  return {
    canEquip: true,
    label: `Equip to ${character.name}`,
    reason: ""
  };
}

function jobMatches(characterJob, jobRestriction) {
  if (!jobRestriction || jobRestriction === "none") {
    return true;
  }

  return characterJob.toLowerCase() === jobRestriction.toLowerCase();
}

function renderItemBonus(label, value) {
  if (!value) {
    return "";
  }

  return `<span>${label} +${value}</span>`;
}

function formatSlotName(slot) {
  return slot
    .replace(/([a-z])([0-9])/g, "$1 $2")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function cssClassToken(value) {
  return String(value || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-");
}

function renderEquipment(characters) {
  const list = document.querySelector("#equipment-list");
  if (!list) {
    return;
  }

  list.innerHTML = "";

  if (characters.length === 0) {
    renderInventoryMemberSwitcher(characters);
    renderSelectedMemberStats(null);
    list.innerHTML = `<p class="muted">No guild members loaded.</p>`;
    return;
  }

  ensureSelectedInventoryCharacter(characters);

  renderInventoryMemberSwitcher(characters);

  const charactersToRender = characters.filter(
    (character) => character.key === selectedInventoryCharacterKey
  );

  for (const character of charactersToRender) {
    renderSelectedMemberStats(character);

    const row = document.createElement("article");
    row.className = "row";

    const slots = Object.entries(character.equipment).map(([slot, item]) => {
      if (item === null) {
        return `
          <div class="equipment-slot empty">
            <span>${slot}</span>
            <strong>Empty</strong>
          </div>
        `;
      }

      return `
        <div class="equipment-slot">
          <span>${slot}</span>
          <strong>${item.name}</strong>
          <small>${item.instance_id}</small>
        </div>
      `;
    }).join("");

    row.innerHTML = `
      <div class="row-title">
        <strong>${character.name}</strong>
        <span class="muted">${character.job}</span>
      </div>
      <div class="equipment-grid">${slots}</div>
    `;

    list.appendChild(row);
  }
}

function renderSelectedMemberStats(character) {
  const panel = document.querySelector("#selected-member-stats");
  if (!panel) {
    return;
  }

  if (!character) {
    panel.innerHTML = "";
    return;
  }

  panel.innerHTML = `
    <div class="panel-subheading">
      <h3>Stats</h3>
      <span class="muted">Level ${character.level} ${character.job}</span>
    </div>
    <div class="stats member-stats-grid">
      <div class="stat"><span>STR</span><strong>${character.strength}</strong></div>
      <div class="stat"><span>INT</span><strong>${character.intelligence}</strong></div>
      <div class="stat"><span>AGI</span><strong>${character.agility}</strong></div>
      <div class="stat"><span>WIS</span><strong>${character.wisdom}</strong></div>
      <div class="stat"><span>HP</span><strong>${character.health}/${character.max_health}</strong></div>
      <div class="stat"><span>MP</span><strong>${character.mana}/${character.max_mana}</strong></div>
      <div class="stat"><span>EXP</span><strong>${character.experience}</strong></div>
    </div>
  `;
}

function renderInventoryMemberSwitcher(characters) {
  const nameDisplay = document.querySelector("#selected-member-name");
  const previousButton = document.querySelector("#previous-member-button");
  const nextButton = document.querySelector("#next-member-button");

  if (!nameDisplay || !previousButton || !nextButton) {
    return;
  }

  if (characters.length === 0) {
    selectedInventoryCharacterKey = "";
    nameDisplay.textContent = "No member";
    previousButton.disabled = true;
    nextButton.disabled = true;
    return;
  }

  const selectedIndex = Math.max(
    0,
    characters.findIndex((character) => character.key === selectedInventoryCharacterKey)
  );
  const selectedCharacter = characters[selectedIndex];

  nameDisplay.textContent = `${selectedCharacter.name} (${selectedCharacter.job})`;
  previousButton.disabled = characters.length <= 1;
  nextButton.disabled = characters.length <= 1;

  previousButton.onclick = () => {
    const previousIndex = (selectedIndex - 1 + characters.length) % characters.length;
    selectedInventoryCharacterKey = characters[previousIndex].key;
    loadState();
  };

  nextButton.onclick = () => {
    const nextIndex = (selectedIndex + 1) % characters.length;
    selectedInventoryCharacterKey = characters[nextIndex].key;
    loadState();
  };
}

function ensureSelectedInventoryCharacter(characters) {
  if (characters.length === 0) {
    selectedInventoryCharacterKey = "";
    return;
  }

  if (!characters.some((character) => character.key === selectedInventoryCharacterKey)) {
    selectedInventoryCharacterKey = characters[0].key;
  }
}

function formatJobRestriction(jobRestriction) {
  if (!jobRestriction || jobRestriction === "none") {
    return "Any";
  }

  return jobRestriction;
}

function renderEventLog(eventLog) {
  const list = document.querySelector("#event-log");
  if (!list) {
    return;
  }

  list.innerHTML = "";

  if (eventLog.length === 0) {
    list.innerHTML = `<p class="muted">No events yet.</p>`;
    return;
  }

  for (const entry of [...eventLog].reverse()) {
    const row = document.createElement("div");
    row.className = "log-entry";
    row.textContent = entry;
    list.appendChild(row);
  }
}

async function startQuest(questKey) {
  if (selectedCharacterKey === "") {
    renderEventLog(["No available members can start a quest."]);
    return;
  }

  const response = await fetch(startQuestUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      quest_key: questKey,
      character_key: selectedCharacterKey
    })
  });

  if (!response.ok) {
    const error = await response.json();
    renderEventLog([error.message]);
    return;
  }

  await loadState();
}

async function equipItem(instanceId) {
  if (selectedInventoryCharacterKey === "") {
    renderEventLog(["Select a guild member before equipping an item."]);
    return;
  }

  const response = await fetch(equipItemUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      character_key: selectedInventoryCharacterKey,
      instance_id: instanceId
    })
  });

  if (!response.ok) {
    const error = await response.json();
    renderEventLog([error.message]);
    return;
  }

  await loadState();
}

async function loadTestFile() {
  await fetch(loadTestFileUrl, {
    method: "POST"
  });
  selectedCharacterKey = "";
  selectedInventoryCharacterKey = "";
  await loadState();
}

async function loadState() {
  const response = await fetch(stateUrl);
  const state = await response.json();

  const guildName = document.querySelector("#guild-name");
  const guildGold = document.querySelector("#guild-gold");

  if (guildName) {
    guildName.textContent = state.guild.name;
  }

  if (guildGold) {
    guildGold.textContent = state.guild.gold;
  }

  renderCharacters(state.characters);
  renderCharacterSelect(state.characters);
  renderQuests(state.quests);
  renderActiveQuests(state.guild.active_quests);
  ensureSelectedInventoryCharacter(state.characters);
  renderInventory(state.guild.inventory, state.characters);
  renderEquipment(state.characters);
  renderEventLog(state.event_log);
}

const loadTestFileButton = document.querySelector("#load-test-file-button");
if (loadTestFileButton) {
  loadTestFileButton.onclick = loadTestFile;
}

loadState();
setInterval(loadState, 1000);
