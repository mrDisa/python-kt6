import time
from app.workers.celery_app import celery_app

@celery_app.task(name="todos.notify_created")
def notify_todo_created(todo_id: int, title: str, recipient: str) -> dict:
    # Demonstration of asynchronous notification delivery; no real email is sent.
    time.sleep(5)
    return {"todo_id": todo_id, "recipient": recipient, "message": f"Task '{title}' was created", "delivered": True}
