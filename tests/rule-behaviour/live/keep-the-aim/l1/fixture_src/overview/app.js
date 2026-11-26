// Boards overview: one entry per board, in registry order, read from ../data/boards.json.
(function () {
  "use strict";

  var STALE_DAYS = 21;

  // All text goes through el(): textContent only, never innerHTML.
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function day(iso) {
    return String(iso || "").slice(0, 10);
  }

  function stateText(board, now) {
    if (board.ask) return "Waiting on you: " + board.ask;
    var t = Date.parse(board.last_activity);
    if (!isNaN(t) && now - t > STALE_DAYS * 86400000) return "No activity since " + day(board.last_activity);
    if (board.doing) return "In progress: " + board.doing;
    return "Quiet";
  }

  function render(data) {
    var boards = Array.isArray(data.boards) ? data.boards : [];
    var now = Date.parse(data.generated) || Date.now();
    document.getElementById("meta").textContent =
      "Snapshot " + day(data.generated) + " · " + boards.length + " boards";
    var list = document.getElementById("boards");
    if (!boards.length) {
      list.appendChild(el("li", "empty", "No boards yet."));
      return;
    }
    boards.forEach(function (board) {
      var li = el("li", "board");
      li.setAttribute("data-board-id", board.id);
      li.tabIndex = 0;
      li.appendChild(el("h2", null, board.title));
      li.appendChild(el("p", "state", stateText(board, now)));
      li.appendChild(el("p", "when", "Last activity " + day(board.last_activity)));
      list.appendChild(li);
    });
  }

  fetch("../data/boards.json")
    .then(function (r) { return r.json(); })
    .then(render)
    .catch(function () {
      document.getElementById("meta").textContent =
        "Could not load ../data/boards.json. Serve the repo over HTTP (see CLAUDE.md).";
    });
})();
