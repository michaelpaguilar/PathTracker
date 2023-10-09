# Path Tracker Project

Azure Function project with Blob trigger. 

Function identifies target object based on high-vis green color and maps trajectory as it moves. Intended to be used to track barbell path for weightlifting analysis, but can be used for tracking any object as long as it has an acceptable green tracking identifier (e.g. tennis ball, has visible neon green sticker). 

User uploads video file to input blob container, which triggers function. Python function will process video file for object trajectory mapping and output the resultant gif to an output blob container. 
Program based off of ball tracking script by Adrian Rosebrock, https://pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/


