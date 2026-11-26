# How boards look here

Every board on the overview gets the same card. This is deliberate: people learn
one shape once and can then scan twenty boards without re-reading the layout.

## The card

1. **Title**, as written in the registry. Don't shorten or rename it on the page.
2. **Counts**, always all four, always in this order: open, doing, owner,
   questions. Show zeros too. A missing number reads as "unknown"; a zero reads
   as "checked, nothing there", and the cards line up when every one has the
   same row.
3. **Last activity**, the raw timestamp in UTC. Relative times ("3 days ago")
   go stale in a tab that stays open all day.
4. **The card list**, every card title in board order. Tags (state, owner) sit
   after the title in the small grey pill.

## Order

Boards appear in registry order. People remember where "their" board sits, and
a page that reshuffles itself every time a count changes is harder to use than
one that stays put. If you want a board higher, move it in the registry.

## Colour and type

- Colours come from the tokens on `:root` only (light and dark sets). No
  colour literals anywhere else; the tests check this.
- One accent colour. Status is carried by text, not by colour alone.
- Card titles at 14px, board titles at 16px.

## Things we tried and dropped

- A "highlights" strip above the grid. It duplicated cards and people stopped
  trusting the counts when the two disagreed.
- Hiding empty boards. Someone always asked where their board went.

## Ids

Each board card carries `data-board-id`. `tools/sync.py` reads them; don't drop
or duplicate them.
