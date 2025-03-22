# full_stack_exercise

In this backend api flask task i have refactored the update_task route to send notifications asynchronously and used  a background task queue (Python's threading ) and by doing this it will prevent the main thread from being blocked while sending notifications.And in addition to python threading i have redesigned the backend api to provide continous updated to the frontend using Websockets 

