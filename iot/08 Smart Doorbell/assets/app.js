const connectionDot=document.getElementById('connection-dot');
const connectionLabel=document.getElementById('connection-label');
const errorContainer=document.getElementById('error-container');
const cameraStream=document.getElementById('camera-stream');
const placeholder=document.getElementById('video-placeholder');
const visitorAlert=document.getElementById('visitor-alert');
const alertText=document.getElementById('alert-text');
const snapshotText=document.getElementById('snapshot-text');
const eventList=document.getElementById('event-list');
const clearEventsButton=document.getElementById('clear-events');
const socket=io(`http://${window.location.host}`);

let firstFrameReceived=false;
let alertTimer=null;

function setConnectionStatus(state,label){
  connectionDot.className=`status-indicator ${state}`;
  connectionLabel.textContent=label;
}

function showCameraFrame(base64Image){
  cameraStream.src=`data:image/jpeg;base64,${base64Image}`;
  if(!firstFrameReceived){
    firstFrameReceived=true;
    placeholder.style.display='none';
    cameraStream.style.display='block';
  }
}

function showDoorbellAlert(){
  visitorAlert.classList.add('active');
  alertText.textContent='Someone is at the door!';
  if(alertTimer) clearTimeout(alertTimer);
  alertTimer=setTimeout(()=>{
    visitorAlert.classList.remove('active');
    alertText.textContent='Waiting for visitors...';
  },5000);
}

function addVisitorEvent(timeValue){
  const empty=eventList.querySelector('.empty-events');
  if(empty) empty.remove();

  const row=document.createElement('div');
  row.className='event-item';

  const time=document.createElement('span');
  time.className='event-time';
  time.textContent=timeValue;

  const message=document.createElement('div');
  message.className='event-message';

  const marker=document.createElement('span');
  marker.className='event-marker';

  const text=document.createElement('span');
  text.textContent='Doorbell pressed';

  message.appendChild(marker);
  message.appendChild(text);
  row.appendChild(time);
  row.appendChild(message);
  eventList.prepend(row);

  const rows=eventList.querySelectorAll('.event-item');
  if(rows.length>10) rows[rows.length-1].remove();
}

socket.on('connect',()=>{
  setConnectionStatus('on','Connected');
  errorContainer.style.display='none';
});

socket.on('disconnect',()=>{
  setConnectionStatus('error','Disconnected');
  errorContainer.textContent='Connection lost. Check the board and run the App again.';
  errorContainer.style.display='block';
});

socket.on('camera_frame',message=>{
  if(message&&message.image) showCameraFrame(message.image);
});

socket.on('doorbell_event',message=>{
  if(!message) return;
  showDoorbellAlert();
  addVisitorEvent(message.time||'--:--:--');
});

socket.on('visitor_photo',message=>{
  if(!message) return;
  const filename=message.filename||'photo';
  const time=message.time||'';
  snapshotText.textContent=`${filename}${time?` · ${time}`:''}`;
});

clearEventsButton.addEventListener('click',()=>{
  eventList.innerHTML='<div class="empty-events">No visitors yet.</div>';
});
