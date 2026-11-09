# Personal to-do list

Say “Add do laundry to my to-do list”, or use `/tdt-todo`. A to-do is a short
personal item that does not belong to a project. To-do items are separate from
software-production tasks, reminders and knowledge. They never appear in knowledge
or scratchpad search.

ThisDamnThing saves each to-do as a Markdown file under `work/todos/`. TDT
creates the folder on first save. A to-do has a title, optional detail text and
a status: `open` or `done`. When you mark a to-do done, TDT records the
completion time. To-do items have no due dates. For a date or time, use a
[reminder](reminders.md).

Ask your agent to list, tick off, reopen or remove to-do items. Done items stay
in the full list until you remove them. Remove deletes the file and cannot be
undone.

## Commands

Run these commands from the workspace root. Replace `ID` with the id from
`tdt todo list`, and `N` with the current `revision` of that item.

```sh
tdt todo add "Do laundry" --user-instruction "Add do laundry"
tdt todo list --status all
tdt todo done ID --revision N --user-instruction "Tick off laundry"
tdt todo reopen ID --revision N --user-instruction "Reopen laundry"
tdt todo remove ID --revision N --user-instruction "Delete laundry"
```

Add optional detail text to `todo add` with `--detail TEXT`. A change with an old revision
fails. Read the item again with `tdt todo show ID` before you retry.

## MCP access

Both MCP profiles expose `tdt_todo_list` and `tdt_todo_read`. The everyday
profile also exposes `tdt_todo_add`, `tdt_todo_done`, `tdt_todo_reopen` and
`tdt_todo_remove`. Each change needs the current `todo_revision`.
