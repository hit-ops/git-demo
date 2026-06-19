from fastapi import FastAPI, HTTPException

from crud import create_todo, delete_todo, get_todo, get_todos, update_todo
from schemas import Todo, TodoCreate

app = FastAPI()


@app.post("/todos", response_model=Todo)
def create_todo_endpoint(todo: TodoCreate):
    existing = get_todo(todo.id)
    if existing:
        raise HTTPException(status_code=400, detail="Todo with this id already exists")
    return create_todo(todo)


@app.get("/todos", response_model=list[Todo])
def get_todos_endpoint():
    return get_todos()


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo_endpoint(todo_id: int):
    todo = get_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo_endpoint(todo_id: int, updated_todo: Todo):
    todo = update_todo(todo_id, updated_todo)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.delete("/todos/{todo_id}")
def delete_todo_endpoint(todo_id: int):
    success = delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
