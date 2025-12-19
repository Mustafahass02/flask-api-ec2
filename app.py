import logging
from flask import Flask, request, jsonify
from datetime import datetime
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


tasks = {}
task_id_counter = 1

@app.route("/health", methods = ['GET'])
def healthcheck():
    logger.info("health check called")
    return jsonify({
        'status' : 'healthy',
        'Timestamp': datetime.now().isoformat
    })
@app.route("/tasks", methods = ['GET'])
def get_tasks():
    logger.info(f"Retrieved {len(tasks)} tasks")
    return jsonify({'tasks' : list(tasks.values())}), 200

@app.route('/tasks', methods =['POST'])
def create_task():
    global task_id_counter
    data = request.get_json()

    if not data or 'title' not in data:
        logger.warning("Task creation failed missing title")
        return jsonify({'error': 'title is required'}), 400
    
    task = {
        'id': task_id_counter,
        'title': data['title'],
        'description' : data.get('description', ''),
        'completed': False,
        'created_at': datetime.now().isoformat()
    }

    tasks[task_id_counter]=task
    logger.info(f"created task {task_id_counter}: {data['title']}")
    task_id_counter +=1

    return jsonify(task), 201


@app.route('/tasks/<int:task_id>', methods = ['GET'])
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        logger.warning(f"Task {task_id} not found")
        return jsonify ({'error': 'task not found'}),400
    
    logger.info(f"task {task_id} retrieved")
    return jsonify(task),200

@app.route('/tasks/<int:task_id>', methods = ['PUT'])
def updatetask(task_id):
    if not task_id:
        return jsonify(f"error : task {task_id} not found")
    
    data = request.get_json()
    task = tasks[task_id]

    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'completed' in data:
        task['completed'] = data['completed']

    task['updated_at'] = datetime.now().isoformat()

    logger.info(f"Updated task {task_id}")
    return jsonify(task),200

@app.route('/tasks/<int:task_id>', methods = ['DELETE'])
def delete_task(task_id):
    if task_id not in tasks:
        return jsonify({'error' : 'Task not found'}), 404
    
    deleted_task = tasks.pop(task_id)
    logger.info(f"deleted task {task_id}")
    return jsonify({'message': 'task deleted', 'task': deleted_task}), 200

if __name__ == '__main__':
    logger.info("starting flask application")
    app.run(host ='0.0.0.0', port=5000, debug=False)
    




