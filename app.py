from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# สถานะของเกม
game_results = []
is_active = False

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/')
def student():
    return render_template('student.html')

# เมื่ออาจารย์สั่งเริ่มเกม
@socketio.on('start_game')
def handle_start():
    global game_results, is_active
    game_results = [] # ล้างผลลัพธ์เก่า
    is_active = True
    emit('game_starting', broadcast=True) # ส่งสัญญาณให้นักเรียนทุกคนนับถอยหลัง

# เมื่อนักเรียนกดปุ่ม
@socketio.on('submit_click')
def handle_click(data):
    global game_results, is_active
    if is_active:
        # เก็บเวลาที่ Server ได้รับ (ความละเอียดระดับไมโครวินาที)
        # ผสมกับเลขสุ่มเล็กน้อยเพื่อแก้ปัญหา timestamp เท่ากันเป๊ะ
        arrival_time = time.time() + random.uniform(0, 0.000001)
        
        # ตรวจสอบว่าชื่อนี้กดไปหรือยัง (ป้องกันการกดซ้ำ)
        if not any(res['name'] == data['name'] for res in game_results):
            result = {
                'name': data['name'],
                'time': arrival_time
            }
            game_results.append(result)
            # เรียงลำดับตามเวลา
            game_results.sort(key=lambda x: x['time'])
            
            # ส่งข้อมูลที่อัปเดตไปให้อาจารย์
            emit('update_leaderboard', game_results, broadcast=True)

# เมื่ออาจารย์สั่งรีเซ็ต
@socketio.on('reset_game')
def handle_reset():
    global game_results, is_active
    game_results = []
    is_active = False
    emit('game_reset', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)