const socket=io(`http://${window.location.host}`);

const dot=document.getElementById('connection-dot');
const connectionText=document.getElementById('connection-text');
const errorBox=document.getElementById('error-container');

const camera=document.getElementById('camera-stream');
const cameraPlaceholder=document.getElementById('camera-placeholder');

const systemSwitch=document.getElementById('system-switch');
const motorSwitch=document.getElementById('motor-switch');

const joystickDot=document.getElementById('joystick-dot');

function n(id,value,digits=1){
  const el=document.getElementById(id);
  const num=Number(value);
  el.textContent=Number.isFinite(num)?num.toFixed(digits):'--';
}

function updateJoystickPad(x,y){
  const cx=512,cy=512;
  const dx=Math.max(-1,Math.min(1,(x-cx)/512));
  const dy=Math.max(-1,Math.min(1,(y-cy)/512));
  const radius=62;

  joystickDot.style.left=`calc(50% - 9px + ${dx*radius}px)`;
  joystickDot.style.top=`calc(50% - 9px + ${dy*radius}px)`;
}

socket.on('connect',()=>{
  dot.className='status-dot on';
  connectionText.textContent='CONNECTED';
  errorBox.style.display='none';
  socket.emit('get_initial_state',{});
});

socket.on('disconnect',()=>{
  dot.className='status-dot error';
  connectionText.textContent='DISCONNECTED';
  errorBox.textContent='Connection lost. Check the board and run the App again.';
  errorBox.style.display='block';
});

socket.on('camera_frame',msg=>{
  if(!msg||!msg.image)return;
  camera.src=`data:image/jpeg;base64,${msg.image}`;
  cameraPlaceholder.style.display='none';
  camera.style.display='block';
});

socket.on('environment_update',d=>{
  if(!d)return;
  n('temperature',d.temperature);
  n('humidity',d.humidity);
  n('distance',d.distance);

  const pir=document.getElementById('pir-status');
  if(d.pir){
    pir.textContent='MOTION DETECTED';
    pir.className='state-motion';
  }else{
    pir.textContent='AREA CLEAR';
    pir.className='state-clear';
  }
});

socket.on('joystick_update',d=>{
  if(!d)return;
  updateJoystickPad(Number(d.x),Number(d.y));
  document.getElementById('pan-angle').textContent=`${d.pan}°`;
  document.getElementById('tilt-angle').textContent=`${d.tilt}°`;
});

socket.on('imu_update',d=>{
  if(!d)return;
  const a=d.accel||[0,0,0],g=d.gyro||[0,0,0],m=d.mag||[0,0,0];
  n('ax',a[0],2);n('ay',a[1],2);n('az',a[2],2);
  n('gx',g[0],2);n('gy',g[1],2);n('gz',g[2],2);
  n('mx',m[0],2);n('my',m[1],2);n('mz',m[2],2);
  n('azimuth',d.azimuth,1);
  n('pressure',d.pressure,1);
  n('altitude',d.altitude,1);
  n('imu-temp',d.imu_temperature,1);
});

socket.on('control_state',d=>{
  if(!d)return;
  systemSwitch.checked=Boolean(d.system_running);
  motorSwitch.checked=Boolean(d.motor_enabled);
  motorSwitch.disabled=!d.system_running;
});

systemSwitch.addEventListener('change',()=>{
  socket.emit('toggle_system',{enabled:systemSwitch.checked});
});

motorSwitch.addEventListener('change',()=>{
  socket.emit('toggle_motor',{enabled:motorSwitch.checked});
});
