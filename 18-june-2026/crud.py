from typing import Optional

from db import conn
from schemas import Todo, TodoCreate


def _row_to_todo(row: tuple) -> Todo:
    return Todo(
        id=row[0],
        title=row[1],
        completed=bool(row[2]),
    )


def create_todo(todo: TodoCreate) -> Todo:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO todos (id, title, completed)
        VALUES (?, ?, ?)
        """,
        (todo.id, todo.title, 1 if todo.completed else 0),
    )
    conn.commit()
    return Todo(**todo.dict())


def get_todos() -> list[Todo]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos")
    rows = cursor.fetchall()
    return [_row_to_todo(row) for row in rows]


def get_todo(todo_id: int) -> Optional[Todo]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id=?", (todo_id,))
    row = cursor.fetchone()
    return _row_to_todo(row) if row else None


def update_todo(todo_id: int, updated_todo: Todo) -> Optional[Todo]:
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE todos
        SET id=?, title=?, completed=?
        WHERE id=?
        """,
        (
            updated_todo.id,
            updated_todo.title,
            1 if updated_todo.completed else 0,
            todo_id,
        ),
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_todo(updated_todo.id)


def delete_todo(todo_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id=?", (todo_id,))
    conn.commit()
    return cursor.rowcount > 0
