from api import app, db, models
from datetime import datetime
count = 0
if count != 1:
    today = datetime.today().date()
    todo = models.Todo(description="Run a marathon", due_date=today, completed=False)
    todo.to_dict()
    db.session.add(todo)
    db.session.commit()
    count += 1

if __name__ == '__main__':
    app.run()
