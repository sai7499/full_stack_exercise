from flask import Flask, jsonify, request, Response
import datetime
import time  # Simulate some work
import threading  # Import threading module for async operations

from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Initialize Flask app and SocketIO
app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

socketio = SocketIO(app, cors_allowed_origins="*")


tasks = [
    {
        "id": 1,
        "title": "Grocery Shopping",
        "completed": False,
        "due_date": "2024-03-15",
    },
    {"id": 2, "title": "Pay Bills", "completed": False, "due_date": "2024-03-20"},
]


# Emit event to notify all connected clients when any CRUD operation is done
def emit_task_update():
    socketio.emit("updated tasks list", {"tasks": tasks})


next_task_id = 3  # For assigning new task IDs


# Function to send notifications (simulating with time.sleep)
def send_email_notification(task_id):
    time.sleep(2)  # Simulate sending a notification (e.g., sending an email)
    print(f"Notification sent for task {task_id}")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def create_task():

    data = request.get_json()
    global next_task_id  # we need to tell python such that the variable we are using here in creating new_task json file was global variable not a local variable prior using the particular variable

    # using default current date for the task if not provided in the request
    due_date = data.get("due_date", datetime.date.today().strftime("%Y-%m-%d"))

    new_task = {
        "id": next_task_id,
        "title": data["title"],
        "completed": False,
        "due_date": due_date,
    }

    # global next_task_id
    next_task_id += 1
    tasks.append(new_task)

    # Emit event after creating a new task
    emit_task_update()
    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    for task in tasks:

        if task["id"] == task_id:

            # here we are updating the fields based on the details passed in the data
            task["title"] = data.get("title", task["title"])
            task["completed"] = data.get("completed", task["completed"])
            task["due_date"] = data.get("due_date", task["due_date"])

            # task.update(data)  # Update task attributes

            # Runing the notification task in a separate thread to prevent the main thread from being blocked while sending notifications.
            email_notification_thread = threading.Thread(
                target=send_email_notification, args=(task_id,)
            )
            email_notification_thread.start()

            emit_task_update() # emiting event with new updated tasks list when user updates any task

            return jsonify(task), 200

    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    # print(tasks)
    for i, task in enumerate(tasks):
        print(i, task)
        if task["id"] == task_id:
            del tasks[i]
            emit_task_update() # emiting event with new updated tasks list when user deletes any task
            return jsonify({"message": "Task deleted"}), 204
    return jsonify({"error": "Task not found"}), 404


# Socket.IO event listener to handle client connections
@socketio.on("connect")
def handle_connect():
    print("Client connected!")
    emit_task_update()  # Send the current task list to the newly connected client


# Handle task update requests from the client
@socketio.on("request_task_update")
def handle_task_update():
    print("Task update requested")
    emit_task_update()  # Emit task update


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected!")






if __name__ == "__main__":
    # Start the Flask app with SocketIO support
    socketio.run(app, debug=True)
