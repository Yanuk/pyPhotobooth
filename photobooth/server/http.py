import threading
import random
import cherrypy
import os
import status
from cherrypy.lib.static import serve_file

# HttpServer used to get latest picture taken, get a random picture 
# or command photobooth to perform some command (show halt message 
# while changing ink, etc.)

class HttpRoot(object):

    def __init__(self, photo_dir, booth_stats, cmdQ):
        self.photo_dir = photo_dir
        self.booth_stats = booth_stats
        self.cmdQ = cmdQ
        self.abs_photo_dir = "%s\\%s" % (os.path.join(os.path.abspath(os.curdir)), photo_dir)

        self.last_latestrand = None
        self.last_rand = None
        
    @cherrypy.expose
    def index(self):
        return """<html>
          <head>
            <link href="/static/style.css" rel="stylesheet"/>
            <script src="/static/script.js"></script>
          </head>
      <body>
        <div id="container">
            <div id="layoutzone" class="zone">
                <div class="zone-header">Nombre</div>
                <a class="button layoutbutton" href="#" id="layout1" onclick="sendKey('2');" ></a>
                <a class="button layoutbutton" href="#" id="layout4" onclick="sendKey('1');" ></a>
            </div>
            <div id="filterzone" class="zone">
                <div class="zone-header">Filtre</div>
                <a class="button filterbutton" href="#" id="filterclassique" onclick="sendKey('x');" ></a>
                <a class="button filterbutton" href="#" id="filternoiretblanc" onclick="sendKey('b');" ></a>
                <a class="button filterbutton" href="#" id="filtersepia" onclick="sendKey('s');" ></a>
            </div>
            <div id="gozone" class="zone">
                <div class="zone-header">Photo !</div>
                <a class="button gobutton" href="takepicture" id="gobutton" ></a>
            </div>
        </div>
      </body>
    </html>"""


    @cherrypy.expose
    def askprint(self):
        return """<html>
          <head>
            <link href="/static/style.css" rel="stylesheet"/>
            <script src="/static/script.js"></script>
          </head>
      <body>
        <div id="container">
            <div id="askprinttext" >Imprimer la photo ?</div>
            <div id="askprintzone" >
                <a class="button askprintbutton" href="#" id="askprintyes" onclick="sendKey('y');rebootIn(1, false);" >Oui</a>
                <a class="button askprintbutton" href="#" id="askprintno" onclick="sendKey('n');rebootIn(1, false);" >Non</a>
            </div>
        </div>
      </body>
    </html>"""


    # Serve the given image file
    @cherrypy.expose
    def picture(self, name):
        return serve_file("%s\\%s" % (self.abs_photo_dir, name))

    # Return latest image(s)
    @cherrypy.expose
    def latest(self, num=1):
        n = max(1, int(num))
        images = self.booth_stats.get_image_roll()
        totalNum = len(images)
        if totalNum == 0:
            return "No pictures taken yet"
        elif n==1:
            return serve_file("%s\\%s" % (self.abs_photo_dir, images[-1]))
        else:
            httpstr = ""
            get = min(totalNum, n)
            pics = images[-get:]
            pics.reverse()
            for pic in pics:
                httpstr += "%s<BR><img width='750' src='http://localhost:8080/picture/%s'><BR><HR>" % (pic, pic)
            return httpstr

    # Return random image
    @cherrypy.expose
    def rand(self):
        images = self.booth_stats.get_image_roll()

        if len(images) > 1:
            randChoice = random.choice(images)
            while randChoice == self.last_rand:
                randChoice = random.choice(images)                
            self.last_rand = randChoice
            return serve_file("%s\\%s" % (self.abs_photo_dir, randChoice))
        elif len(images) == 1:
            return self.latest(1)
        else:
            return "No pictures taken yet"

    # If there's a new image, return latest image or else return a random image
    @cherrypy.expose
    def latestrand(self):
        images = self.booth_stats.get_image_roll();
        latestImg = images[-1]
        if self.last_latestrand == latestImg:
            return self.rand();
        else:
            self.last_latestrand = latestImg
            return serve_file("%s\\%s" % (self.abs_photo_dir, latestImg))

    # Return photobooth stats
    @cherrypy.expose
    def stats(self):
        httpstr = "Session start: %s<BR>Pictures taken: %d" % (self.booth_stats.get_session_start(), self.booth_stats.get_session_count())
        return httpstr

    # Put photobooth in maintenance mode
    @cherrypy.expose
    def brb(self):
        self.cmdQ.put("BRB")
        return "BRB cmd sent"

    # Resume normal photobooth operations
    @cherrypy.expose
    def resume(self):
        self.cmdQ.put("RESUME")
        return "RESUME cmd sent"

    # Send virtual keypress to photobooth
    @cherrypy.expose
    def vkey(self, key=None):
        if key is not None:
            cmd = "VKEY:%s" % key
            self.cmdQ.put(cmd)
            return "%s cmd sent" % (cmd)
        else:
            return "No key given"

    # Send virtual keypress to photobooth
    @cherrypy.expose
    def takepicture(self):
        cmd = "TAKEPICTURE"
        self.cmdQ.put(cmd)
        return """<html>
          <head>
            <link href="/static/style.css" rel="stylesheet"/>
            <script src="/static/script.js"></script>
            <meta http-equiv="refresh" content="2; url=/checkstatus">
          </head>
      <body>
        <div id="container">
            <div id="waitingtext">Prise de vue en cours...</div>
        </div>
      </body>
    </html>"""

    # Check if ready
    @cherrypy.expose
    def checkstatus(self):
        if status.STATUS == 'Idle' :
            return """<head><meta http-equiv="refresh" content="0; url=/"></head>"""
        elif status.STATUS == 'Askprint' :
            return """<head><meta http-equiv="refresh" content="0; url=/askprint"></head>"""
        elif status.STATUS == 'Picture' :
            return """<html>
              <head>
                <link href="/static/style.css" rel="stylesheet"/>
                <script src="/static/script.js"></script>
                <meta http-equiv="refresh" content="1; url=/checkstatus">
              </head>
          <body>
            <div id="container">
                <div id="waitingtext">Prise de vue en cours...</div>
            </div>
          </body>
        </html>"""
        


class HttpServer(threading.Thread):
    
    def __init__(self, photo_dir, booth_stats, cmdQ):
        self.photo_dir = photo_dir
        self.booth_stats = booth_stats
        self.cmdQ = cmdQ
        random.seed()
        threading.Thread.__init__(self)
        
    def run(self):
        cherrypy.server.socket_host = '0.0.0.0'
        conf = {
             '/': {
                 'tools.sessions.on': True,
                 'tools.staticdir.root': os.path.abspath(os.getcwd())
             },
             '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': './webpublic'
             }
         }
        cherrypy.quickstart(HttpRoot(self.photo_dir, self.booth_stats, self.cmdQ), '/', conf)
        
    def stop(self):
        cherrypy.engine.exit()
