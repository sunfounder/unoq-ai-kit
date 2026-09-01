const socket=io(`http://${window.location.host}`);
const $=id=>document.getElementById(id);

const wheel=$("color-wheel"),ctx=wheel.getContext("2d"),indicator=$("wheel-indicator");
const brightnessSlider=$("brightness-slider");
const RADIUS=90,CENTER=90;
let hue=0,saturation=0,brightness=100,isDragging=false;
let lastSent={r:-1,g:-1,b:-1};
let serverRgb={r:0,g:0,b:0};

function hsvToRgb(h,s,v){const f=(h%360)/60,i=Math.floor(f)%6,p=v*(1-s),q=v*(1-(f-i)*s),t=v*(1-(1-(f-i))*s);let r,g,b;switch(i){case 0:r=v;g=t;b=p;break;case 1:r=q;g=v;b=p;break;case 2:r=p;g=v;b=t;break;case 3:r=p;g=q;b=v;break;case 4:r=t;g=p;b=v;break;default:r=v;g=p;b=q}return{r:Math.round(r*255),g:Math.round(g*255),b:Math.round(b*255)}}
function rgbToHex(r,g,b){return"#"+[r,g,b].map(c=>c.toString(16).padStart(2,"0")).join("")}
function drawWheel(){const size=RADIUS*2,img=ctx.createImageData(size,size),d=img.data;for(let y=0;y<size;y++)for(let x=0;x<size;x++){const dx=x-CENTER,dy=y-CENTER,dist=Math.sqrt(dx*dx+dy*dy);if(dist>RADIUS)continue;const h=(Math.atan2(dy,dx)*180/Math.PI+360)%360,s=Math.min(dist/RADIUS,1),c=hsvToRgb(h,s,1),i=(y*size+x)*4;d[i]=c.r;d[i+1]=c.g;d[i+2]=c.b;d[i+3]=255}ctx.putImageData(img,0,0)}
function moveIndicator(h,s){const a=h*Math.PI/180,d=s*RADIUS;indicator.style.left=CENTER+d*Math.cos(a)+"px";indicator.style.top=CENTER+d*Math.sin(a)+"px"}
function currentRgb(){return hsvToRgb(hue,saturation,brightness/100)}
function displayRgb(r,g,b){$("rgb-values").innerHTML=`R: ${r} &nbsp; G: ${g} &nbsp; B: ${b}`;$("hex-value").textContent=rgbToHex(r,g,b)}
function sendRgb(r,g,b){if(r===lastSent.r&&g===lastSent.g&&b===lastSent.b)return;lastSent={r,g,b};socket.emit("set_rgb_color",{r,g,b})}
function pos(e){const rect=wheel.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX),y=(e.touches?e.touches[0].clientY:e.clientY);return{x:(x-rect.left)*wheel.width/rect.width,y:(y-rect.top)*wheel.height/rect.height}}
function updateFromPos(p){const dx=p.x-CENTER,dy=p.y-CENTER,dist=Math.sqrt(dx*dx+dy*dy);hue=(Math.atan2(dy,dx)*180/Math.PI+360)%360;saturation=Math.min(dist/RADIUS,1);moveIndicator(hue,saturation);const c=currentRgb();displayRgb(c.r,c.g,c.b);sendRgb(c.r,c.g,c.b)}
function start(e){isDragging=true;updateFromPos(pos(e));e.preventDefault()}
function move(e){if(!isDragging)return;updateFromPos(pos(e));e.preventDefault()}
function end(){isDragging=false}
function brightnessChanged(){brightness=parseInt(brightnessSlider.value);const c=currentRgb();displayRgb(c.r,c.g,c.b);sendRgb(c.r,c.g,c.b)}

socket.on("connect",()=>socket.emit("get_initial_state",{}));
socket.on("camera_frame",d=>$("cameraImage").src="data:image/jpeg;base64,"+d.image);
socket.on("camera_control_update",d=>{
 $("panValue").textContent=d.pan+"°"; $("tiltValue").textContent=d.tilt+"°"; $("joystickValue").textContent=`${d.x}, ${d.y}`;
 const x=Math.max(0,Math.min(1023,Number(d.x)||512)), y=Math.max(0,Math.min(1023,Number(d.y)||512));
 $("joystickDot").style.left=(20+(x/1023)*60)+"%";
 $("joystickDot").style.top=(80-(y/1023)*60)+"%";
});
socket.on("room_state",d=>{
 $("temperature").textContent=d.temperature==null?"--°C":d.temperature.toFixed(1)+"°C";
 $("humidity").textContent=d.humidity==null?"--%":d.humidity.toFixed(1)+"%";
 $("motion").textContent=d.motion?"DETECTED":"CLEAR";
 $("ambientLight").textContent=d.light_percent==null?"--%":d.light_percent+"%";
 $("lightLabel").textContent=d.light_label||"Waiting";
 $("lightBar").style.width=(d.light_percent||0)+"%";
 $("autoMode").classList.toggle("active",d.fan_mode==="auto");
 $("manualMode").classList.toggle("active",d.fan_mode==="manual");
 $("fanToggle").checked=!!d.fan_enabled;$("fanToggle").disabled=d.fan_mode!=="manual";
 serverRgb=d.rgb||{r:0,g:0,b:0};displayRgb(serverRgb.r,serverRgb.g,serverRgb.b);
 $("lightToggle").checked=!!(serverRgb.r||serverRgb.g||serverRgb.b);
 lastSent={...serverRgb};
});
socket.on("voice_state",d=>{const listening=d.state==="listening";$("voiceButton").disabled=listening;$("voiceButton").textContent=listening?"🎤 LISTENING...":"🎤 SPEAK";$("voiceText").textContent=listening?"Listening for 4 seconds...":(d.text?`Recognized: "${d.text}"`:"Ready for another command.")});

$("autoMode").onclick=()=>socket.emit("set_fan_mode",{mode:"auto"});
$("manualMode").onclick=()=>socket.emit("set_fan_mode",{mode:"manual"});
$("fanToggle").onchange=e=>socket.emit("toggle_fan",{enabled:e.target.checked});
$("lightToggle").onchange=e=>socket.emit("toggle_light",{enabled:e.target.checked});
$("voiceButton").onclick=()=>socket.emit("voice_control",{});
brightnessSlider.oninput=brightnessChanged;
wheel.addEventListener("mousedown",start);document.addEventListener("mousemove",move);document.addEventListener("mouseup",end);
wheel.addEventListener("touchstart",start,{passive:false});document.addEventListener("touchmove",move,{passive:false});document.addEventListener("touchend",end);

drawWheel();moveIndicator(0,0);displayRgb(0,0,0);
