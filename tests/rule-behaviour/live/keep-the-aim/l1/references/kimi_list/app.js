// Boards overview: an owner-first list with every dependency written as a sentence.
(function () {
  "use strict";

  var STALE_DAYS = 21;

  // All data-derived text goes through el(): textContent only, never innerHTML.
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function clean(value) {
    return value === undefined || value === null ? "" : String(value).trim();
  }

  function day(iso) {
    return clean(iso).slice(0, 10);
  }

  function plural(count, singular, pluralForm) {
    return count + " " + (count === 1 ? singular : (pluralForm || singular + "s"));
  }

  function isStale(board, now) {
    var t = Date.parse(board.last_activity);
    return !isNaN(t) && now - t > STALE_DAYS * 86400000;
  }

  function stateText(record, now) {
    if (record.ask) return "Needs you: " + record.ask;
    if (isStale(record.board, now)) {
      return "No activity since " + (day(record.board.last_activity) || "the last recorded activity");
    }
    var doing = clean(record.board.doing);
    if (doing) return "In progress: " + doing;
    return "Quiet";
  }

  function dependencyText(dependency) {
    var text = dependency.from.title + " is waiting on " + dependency.to.title;
    if (dependency.why) text += ": " + dependency.why;
    if (!/[.!?]$/.test(text)) text += ".";
    return text;
  }

  function joinNames(names) {
    if (names.length < 2) return names[0] || "";
    if (names.length === 2) return names[0] + " and " + names[1];
    return names.slice(0, -1).join(", ") + ", and " + names[names.length - 1];
  }

  function impactText(record) {
    var names = record.holdingUp.map(function (dependency) {
      return dependency.from.title;
    });
    if (names.length === 1) return "This board is holding up " + names[0] + ".";
    return "This board is holding up " + plural(names.length, "board") + ": " + joinNames(names) + ".";
  }

  function summaryText(records) {
    var needsInput = records.filter(function (record) { return Boolean(record.ask); }).length;
    var sentences = [];
    if (needsInput) {
      sentences.push(needsInput === 1 ? "1 board needs your input" : needsInput + " boards need your input");
    } else {
      sentences.push("Nothing needs your input");
    }

    var biggestBlocker = records.slice().sort(function (a, b) {
      return b.holdingUp.length - a.holdingUp.length || a.index - b.index;
    })[0];
    if (biggestBlocker && biggestBlocker.holdingUp.length) {
      sentences.push(
        biggestBlocker.title + " is holding up " + plural(biggestBlocker.holdingUp.length, "board")
      );
    } else {
      sentences.push("No dependencies are recorded");
    }
    return sentences.join(". ") + ".";
  }

  function render(data) {
    data = data && typeof data === "object" ? data : {};
    var boards = Array.isArray(data.boards) ? data.boards : [];
    var links = Array.isArray(data.links) ? data.links : [];
    var parsedNow = Date.parse(data.generated);
    var now = isNaN(parsedNow) ? Date.now() : parsedNow;
    var byId = new Map();
    var validLinks = [];

    var records = boards.map(function (board, index) {
      board = board && typeof board === "object" ? board : {};
      var record = {
        board: board,
        index: index,
        id: clean(board.id),
        title: clean(board.title) || "Untitled board",
        ask: clean(board.ask),
        waitingOn: [],
        holdingUp: []
      };
      byId.set(record.id, record);
      return record;
    });

    links.forEach(function (link) {
      if (!link || typeof link !== "object") return;
      var from = byId.get(clean(link.from));
      var to = byId.get(clean(link.to));
      if (!from || !to) return;
      var dependency = { from: from, to: to, why: clean(link.why) };
      from.waitingOn.push(dependency);
      to.holdingUp.push(dependency);
      validLinks.push(dependency);
    });

    records.forEach(function (record) {
      record.waitingOn.sort(function (a, b) { return a.to.index - b.to.index; });
      record.holdingUp.sort(function (a, b) { return a.from.index - b.from.index; });
    });

    document.getElementById("meta").textContent =
      "Snapshot " + (day(data.generated) || "date unknown") + " · " +
      plural(records.length, "board") + " · " + plural(validLinks.length, "connection");

    var summary = document.getElementById("summary");
    summary.hidden = !records.length;
    document.getElementById("summary-text").textContent = records.length ? summaryText(records) : "";

    var list = document.getElementById("boards");
    list.textContent = "";
    if (!records.length) {
      list.appendChild(el("li", "empty", "No boards yet."));
      return;
    }

    records.slice().sort(function (a, b) {
      if (Boolean(a.ask) !== Boolean(b.ask)) return a.ask ? -1 : 1;
      return b.holdingUp.length - a.holdingUp.length || a.index - b.index;
    }).forEach(function (record) {
      var li = el("li", "board" + (record.ask ? " needs-you" : ""));
      li.setAttribute("data-board-id", record.id);
      li.tabIndex = 0;

      if (record.ask || record.holdingUp.length) {
        var badges = el("div", "badges");
        if (record.ask) badges.appendChild(el("span", "badge needs", "Needs you"));
        if (record.holdingUp.length) {
          badges.appendChild(el(
            "span",
            "badge holds",
            "Holding up " + plural(record.holdingUp.length, "board")
          ));
        }
        li.appendChild(badges);
      }

      li.appendChild(el("h3", null, record.title));
      li.appendChild(el("p", "state", stateText(record, now)));
      li.appendChild(el(
        "p",
        "when",
        day(record.board.last_activity) ?
          "Last activity " + day(record.board.last_activity) :
          "No activity date recorded"
      ));

      if (record.holdingUp.length) {
        li.appendChild(el("p", "impact", impactText(record)));
      }

      if (record.waitingOn.length) {
        var dependencies = el("section", "dependencies");
        dependencies.appendChild(el("h4", null, "What’s holding it up"));
        var connections = el("ul", "connections");
        record.waitingOn.forEach(function (dependency) {
          connections.appendChild(el("li", "connection", dependencyText(dependency)));
        });
        dependencies.appendChild(connections);
        li.appendChild(dependencies);
      }

      list.appendChild(li);
    });
  }

  fetch("../data/boards.json")
    .then(function (response) {
      if (!response.ok) throw new Error("Could not load boards");
      return response.json();
    })
    .then(render)
    .catch(function () {
      document.getElementById("summary").hidden = true;
      document.getElementById("boards").textContent = "";
      document.getElementById("meta").textContent =
        "Could not load ../data/boards.json. Serve the repo over HTTP (see CLAUDE.md).";
    });
})();
