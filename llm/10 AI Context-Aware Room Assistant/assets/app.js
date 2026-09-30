// SPDX-License-Identifier: MPL-2.0
const socket=io(`http://${window.location.host}`),el=id=>document.getElementById(id);
const cameraStream=el('camera-stream'),speakButton=el('speak-button');
let busy=false,streamRetryTimer=null;
const titles={ready:'Ready',listening:'Listening',recognizing:'Recognizing Speech',sensors:'Reading Sensors',thinking:'AI Is Creating a Scene',applying:'Applying Light',speaking:'Speaking',error:'Something Went Wrong'};

// Room light: the same adjustable control as the smart-room project.
const wheel=el('color-wheel'),ctx=wheel.getContext('2d'),indicator=el('wheel-indicator');
const brightnessSlider=el('brightness-slider'),lightToggle=el('lightToggle');
const RADIUS=75,CENTER=75;
let hue=0,saturation=0,brightness=100,isDragging=false,lastSent={r:-1,g:-1,b:-1},lastSentBrightness=-1;

function hsvToRgb(h,s,v){const f=(h%360)/60,i=Math.floor(f)%6,p=v*(1-s),q=v*(1-(f-i)*s),t=v*(1-(1-(f-i))*s);let r,g,b;switch(i){case 0:r=v;g=t;b=p;break;case 1:r=q;g=v;b=p;break;case 2:r=p;g=v;b=t;break;case 3:r=p;g=q;b=v;break;case 4:r=t;g=p;b=v;break;default:r=v;g=p;b=q}return{r:Math.round(r*255),g:Math.round(g*255),b:Math.round(b*255)}}
function rgbToHsv(r,g,b){r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min;let h=0;if(d>0){if(max===r)h=60*(((g-b)/d)%6);else if(max===g)h=60*((b-r)/d+2);else h=60*((r-g)/d+4)}if(h<0)h+=360;return{h:h,s:max>0?d/max:0,v:max}}
function rgbToHex(r,g,b){return'#'+[r,g,b].map(c=>c.toString(16).padStart(2,'0')).join('')}
function drawWheel(){const size=RADIUS*2,img=ctx.createImageData(size,size),d=img.data;for(let y=0;y<size;y++)for(let x=0;x<size;x++){const dx=x-CENTER,dy=y-CENTER,dist=Math.sqrt(dx*dx+dy*dy);if(dist>RADIUS)continue;const h=(Math.atan2(dy,dx)*180/Math.PI+360)%360,s=Math.min(dist/RADIUS,1),c=hsvToRgb(h,s,1),i=(y*size+x)*4;d[i]=c.r;d[i+1]=c.g;d[i+2]=c.b;d[i+3]=255}ctx.putImageData(img,0,0)}
function moveIndicator(h,s){const a=h*Math.PI/180,d=s*RADIUS;indicator.style.left=CENTER+d*Math.cos(a)+'px';indicator.style.top=CENTER+d*Math.sin(a)+'px'}
function currentRgb(){const c=hsvToRgb(hue,saturation,brightness/100);return{r:Math.round(c.r*100/255),g:Math.round(c.g*100/255),b:Math.round(c.b*100/255)}}
function displayRgb(r,g,b){el('rgb-values').textContent=`R ${r} · G ${g} · B ${b}`;el('hex-value').textContent=rgbToHex(Math.round(r*2.55),Math.round(g*2.55),Math.round(b*2.55))}
function sendRgb(r,g,b){if(r===lastSent.r&&g===lastSent.g&&b===lastSent.b&&brightness===lastSentBrightness)return;lastSent={r,g,b};lastSentBrightness=brightness;socket.emit('set_rgb_color',{r,g,b,brightness})}
function pointerPos(e){const rect=wheel.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX),y=(e.touches?e.touches[0].clientY:e.clientY);return{x:(x-rect.left)*wheel.width/rect.width,y:(y-rect.top)*wheel.height/rect.height}}
function updateFromPos(p){const dx=p.x-CENTER,dy=p.y-CENTER,dist=Math.sqrt(dx*dx+dy*dy);hue=(Math.atan2(dy,dx)*180/Math.PI+360)%360;saturation=Math.min(dist/RADIUS,1);if(brightness===0){brightness=100;brightnessSlider.value=100}moveIndicator(hue,saturation);const c=currentRgb();displayRgb(c.r,c.g,c.b);sendRgb(c.r,c.g,c.b)}
function startDrag(e){isDragging=true;updateFromPos(pointerPos(e));e.preventDefault()}
function moveDrag(e){if(!isDragging)return;updateFromPos(pointerPos(e));e.preventDefault()}
function endDrag(){isDragging=false}
function brightnessChanged(){brightness=parseInt(brightnessSlider.value);const c=currentRgb();displayRgb(c.r,c.g,c.b);sendRgb(c.r,c.g,c.b)}
// Move the control to whatever the AI (or another browser) has set.
function applyServerLight(data){if(isDragging)return;const r=Number(data.red||0),g=Number(data.green||0),b=Number(data.blue||0);brightness=Number(data.brightness||0);const hsv=rgbToHsv(Math.round(r*2.55),Math.round(g*2.55),Math.round(b*2.55));hue=hsv.h;saturation=hsv.s;brightnessSlider.value=brightness;moveIndicator(hue,saturation);displayRgb(r,g,b);lightToggle.checked=!!(r||g||b);lastSent={r,g,b};lastSentBrightness=brightness}

brightnessSlider.oninput=brightnessChanged;
lightToggle.onchange=e=>socket.emit('toggle_light',{enabled:e.target.checked});
wheel.addEventListener('mousedown',startDrag);document.addEventListener('mousemove',moveDrag);document.addEventListener('mouseup',endDrag);
wheel.addEventListener('touchstart',startDrag,{passive:false});document.addEventListener('touchmove',moveDrag,{passive:false});document.addEventListener('touchend',endDrag);
drawWheel();moveIndicator(0,0);displayRgb(0,0,0);

function loadCameraStream(){clearTimeout(streamRetryTimer);cameraStream.src=`http://${window.location.hostname}:7000/stream?r=${Date.now()}`;}
cameraStream.addEventListener('error',()=>{clearTimeout(streamRetryTimer);streamRetryTimer=setTimeout(loadCameraStream,1500);});
function update(data){
  const state=data.state||'ready';busy=Boolean(data.busy)||['listening','recognizing','sensors','thinking','applying','speaking'].includes(state);
  el('voice-panel').className=`voice-inline ${state}`;el('status-title').textContent=titles[state]||state;el('status-message').textContent=data.message||'';
  speakButton.disabled=!socket.connected||busy;speakButton.classList.toggle('listening',state==='listening');el('button-label').textContent=state==='listening'?`LISTENING ${data.seconds||''}`:'SPEAK';
  el('temperature').textContent=data.temperature||'Unavailable';el('humidity').textContent=data.humidity||'Unavailable';
  const motion=data.motion||'UNKNOWN';el('motion').textContent=motion;el('motion-icon').textContent=motion==='DETECTED'?'●':'◌';el('motion-icon').classList.toggle('detected',motion==='DETECTED');
  if(data.heard)el('heard-text').textContent=data.heard;if(data.reply)el('reply-text').textContent=data.reply;
  el('scene-name').textContent=data.scene||'READY';
  applyServerLight(data);
  el('error-container').textContent=state==='error'?(data.message||'Unknown error'):'';el('error-container').style.display=state==='error'?'block':'none';
}
speakButton.addEventListener('click',()=>{if(socket.connected&&!busy){busy=true;speakButton.disabled=true;socket.emit('start_scene_request',{});}});
socket.on('connect',()=>{el('status-dot').className='status-indicator on';el('connection-label').textContent='CONNECTED';loadCameraStream();socket.emit('get_state',{});});
socket.on('assistant_status',update);
socket.on('disconnect',()=>{clearTimeout(streamRetryTimer);cameraStream.removeAttribute('src');el('status-dot').className='status-indicator error';el('connection-label').textContent='DISCONNECTED';update({state:'error',message:'Connection to the app was lost.'});});
