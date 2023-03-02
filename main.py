import cv2
import math
import time

class Horizon:

    def __init__(self, points = [(0,0),(400,400)], center = (200,200)):
        self.points = points
        self.center = center
        self.radianConverter = math.pi/180
    
    def rotateRadian(self, angleRadian):
        self.points[0] = ( 
            (
                (self.points[0][0] - self.center[0]) * math.cos(angleRadian) - (self.points[0][1] - self.center[1]) * math.sin(angleRadian) + self.center[0],
                (self.points[0][0] - self.center[0]) * math.sin(angleRadian) + (self.points[0][1] - self.center[1]) * math.cos(angleRadian) + self.center[1]
            
            )
        )

        self.points[1] = ( 
            (
                (self.points[1][0] - self.center[0]) * math.cos(angleRadian) - (self.points[1][1] - self.center[1]) * math.sin(angleRadian) + self.center[0],
                (self.points[1][0] - self.center[0]) * math.sin(angleRadian) + (self.points[1][1] - self.center[1]) * math.cos(angleRadian) + self.center[1]
            
            )
        )

    
    def rotateDegree(self, angleDegree):
        self.rotateRadian( angleDegree * self.radianConverter )
    
    def draw(self, frame, color, thickness):
        cv2.line(frame, (int(self.points[0][0]), int(self.points[0][1])), (int(self.points[1][0]), int(self.points[1][1])), color, thickness)        

class Application:

    def __init__(self, cameraIndex = 0, windowTitle = "Video", stopKey = "q", capResolution = {"width":1920, "height":1080}):
        self.video = cv2.VideoCapture(cameraIndex)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, capResolution["width"])
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, capResolution["height"])

        w = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_num = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.target = cv2.VideoWriter('res.avi',fourcc,16,(frame_width,frame_height))

        self.title = windowTitle
        self.stopKey = ord(stopKey)
        self.noDataCount = 0
        self.alpha = 0
        self.state = 1
        self.fixed_fps = 30
        self.fps_data = 1 / self.fixed_fps
        self.currentTime = 0
        self.previusTime = 0


        
        w_hide = math.sqrt( (w/2)**2 + (h/2)**2 ) - w/2
        h_hide = math.sqrt( (w/2)**2 + (h/2)**2 ) - h/2

        self.horizon = Horizon(
            points = [ (0 - w_hide, h/2), (w + w_hide, h/2) ],
            center = ( w/2, h/2 )
        )

    def Draw(self, frame, realFps):
        self.horizon.draw(frame, (0,0,155), 4)
        cv2.putText(frame, "FPS    : "+str(realFps), (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "Degree : "+str(self.alpha), (0  , 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)

        self.horizon.rotateDegree(self.state)

        self.alpha += self.state

        if self.alpha > 10:
            self.state = -1
        elif self.alpha < -10:
            self.state = 1

        time.sleep(self.fps_data)
        self.SaveFrame(frame)

    def SaveFrame(self, frame):
        self.target.write(frame)
    
    def Start(self):
        
        while True:
            self.currentTime = time.time()
            isValid, frame = self.video.read()

            if isValid:
                fps = int( 1  / (self.currentTime - self.previusTime) )
                self.previusTime = self.currentTime

                self.Draw(frame, fps)

                cv2.imshow(self.title, frame)
            else:
                self.noDataCount += 1
                print(f"No image data received for {self.noDataCount} times")
            
            if cv2.waitKey(1) & 0xFF == self.stopKey:
                self.video.release()
                self.target.release()
                cv2.destroyAllWindows()
                break


app = Application()
app.Start()
