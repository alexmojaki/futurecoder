function isVisible(el) {
  var r = el.getBoundingClientRect();
  return r.top + r.height >= 0 && r.left + r.width >= 0 && r.bottom - r.height <= (window.innerHeight || document.documentElement.clientHeight) && r.right - r.width <= (window.innerWidth || document.documentElement.clientWidth);
}

function Star(x, y, z) {
  this.x = x;
  this.y = y;
  this.z = z;
  this.size = 0.5 + Math.random();
}

function WarpSpeed(config) {
  this.SPEED = config.speed == undefined || config.speed < 0 ? 0.7 : config.speed;
  this.TARGET_SPEED = config.targetSpeed == undefined || config.targetSpeed < 0 ? this.SPEED : config.targetSpeed;
  this.SPEED_ADJ_FACTOR = config.speedAdjFactor == undefined ? 0.03 : config.speedAdjFactor < 0 ? 0 : config.speedAdjFactor > 1 ? 1 : config.speedAdjFactor;
  this.DENSITY = config.density == undefined || config.density <= 0 ? 0.7 : config.density;
  this.USE_CIRCLES = config.shape == undefined ? true : config.shape == "circle";
  this.DEPTH_ALPHA = config.depthFade == undefined ? true : config.depthFade;
  this.WARP_EFFECT = config.warpEffect == undefined ? true : config.warpEffect;
  this.WARP_EFFECT_LENGTH = config.warpEffectLength == undefined ? 5 : config.warpEffectLength < 0 ? 0 : config.warpEffectLength;
  this.STAR_SCALE = config.starSize == undefined || config.starSize <= 0 ? 3 : config.starSize;
  this.BACKGROUND_COLOR = config.backgroundColor == undefined ? "hsl(263,45%,7%)" : config.backgroundColor;
  // canvas.width=1; canvas.height=1;
  canvas.width = (canvas.clientWidth < 10 ? 10 : canvas.clientWidth) * (window.devicePixelRatio || 1);
  canvas.height = (canvas.clientHeight < 10 ? 10 : canvas.clientHeight) * (window.devicePixelRatio || 1);
  this.size = (canvas.height < canvas.width ? canvas.height : canvas.width) / (10 / (this.STAR_SCALE <= 0 ? 0 : this.STAR_SCALE));
  this.maxLineWidth = this.size / 30;

  this.STAR_COLOR = config.starColor == undefined ? "#FFFFFF" : config.starColor;
  // this.prevW=-1; this.prevH=-1; //width and height will be set at first draw call
  this.stars = [];
  for (var i = 0; i < this.DENSITY * 1000; i++) {
    this.stars.push(new Star((Math.random() - 0.5) * 1000, (Math.random() - 0.5) * 1000, 1000 * Math.random()));
  }
  this.lastMoveTS = performance.now();
  this.drawRequest = null;
  this.LAST_RENDER_T = 0;
  this.draw();
}

WarpSpeed.prototype = {
  constructor: WarpSpeed,
  draw: function () {
    var TIME = performance.now();
    this.move();
    // if(isVisible(canvas)){
    // if(this.prevW!=canvas.clientWidth||this.prevH!=canvas.clientHeight){
    // 	canvas.width=(canvas.clientWidth<10?10:canvas.clientWidth)*(window.devicePixelRatio||1);
    // 	canvas.height=(canvas.clientHeight<10?10:canvas.clientHeight)*(window.devicePixelRatio||1);
    // }
    // this.size=(canvas.height<canvas.width?canvas.height:canvas.width)/(10/(this.STAR_SCALE<=0?0:this.STAR_SCALE));
    // if(this.WARP_EFFECT) this.maxLineWidth=this.size/30;
    var ctx = canvas.getContext("2d");
    ctx.globalAlpha = 1.0;
    ctx.fillStyle = this.BACKGROUND_COLOR;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = this.STAR_COLOR;
    for (var i = 0; i < this.stars.length; i++) {
      var s = this.stars[i];
      var xOnDisplay = s.x / s.z, yOnDisplay = s.y / s.z;
      var size = s.size * this.size / s.z;
      if (size < 0.3) continue; //don't draw very small dots
      var alpha = (1000 - s.z) / 1000;
      ctx.globalAlpha = alpha < 0 ? 0 : alpha > 1 ? 1 : alpha;
      ctx.beginPath();
      var x2OnDisplay = s.x / (s.z + this.WARP_EFFECT_LENGTH * this.SPEED),
        y2OnDisplay = s.y / (s.z + this.WARP_EFFECT_LENGTH * this.SPEED);
      if (x2OnDisplay < -0.5 || x2OnDisplay > 0.5 || y2OnDisplay < -0.5 || y2OnDisplay > 0.5) continue;
      ctx.moveTo(canvas.width * (xOnDisplay + 0.5) - size / 2, canvas.height * (yOnDisplay + 0.5) - size / 2);
      ctx.lineTo(canvas.width * (x2OnDisplay + 0.5) - size / 2, canvas.height * (y2OnDisplay + 0.5) - size / 2);
      ctx.lineWidth = size > this.maxLineWidth ? this.maxLineWidth : size;
      ctx.lineCap = "butt"
      ctx.strokeStyle = ctx.fillStyle;
      ctx.stroke();
    }
    // this.prevW=canvas.clientWidth;
    // this.prevH=canvas.clientHeight;
    // }
    if (this.drawRequest != -1) this.drawRequest = requestAnimationFrame(this.draw.bind(this));
    this.LAST_RENDER_T = performance.now() - TIME;
  },
  move: function () {
    var t = performance.now(), speedMulF = (t - this.lastMoveTS) / (1000 / 60);
    this.lastMoveTS = t;
    var speedAdjF = Math.pow(this.SPEED_ADJ_FACTOR < 0 ? 0 : this.SPEED_ADJ_FACTOR > 1 ? 1 : this.SPEED_ADJ_FACTOR, 1 / speedMulF);
    this.SPEED = this.TARGET_SPEED * speedAdjF + this.SPEED * (1 - speedAdjF);
    if (this.SPEED < 0) this.SPEED = 0;
    var speed = this.SPEED * speedMulF;
    for (var i = 0; i < this.stars.length; i++) {
      var s = this.stars[i];
      s.z -= speed;
      while (s.z < 1) {
        s.z += 1000;
        s.x = (Math.random() - 0.5) * s.z;
        s.y = (Math.random() - 0.5) * s.z;
      }
    }
  },
}
