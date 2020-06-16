import pyrebase
from pyyoutube import Api
from urllib.parse import urlparse, parse_qs
# credentials for using firebase and youtube API
from vdoApp.utils.credentials import apiKey, config


api = Api(api_key=apiKey)               # API key for youtube
firebase = pyrebase.initialize_app(config)      # firebase object
authe = firebase.auth()
db = firebase.database()                        # database from firebase
baseUrl = "https://www.youtube.com/embed/"      # for embedding on site
baseVideoLink = "https://www.youtube.com/watch?v="  # original watch link



def load30Videos():
    """
    Name: Load 30 Videos
    Task: Take 30 most popular videos from US and add them to the database(firebase)

    Helps in populating the database faster for testing
    """
    noOfVideos = 30
    video_by_chart = api.get_videos_by_chart(
        chart="mostPopular", region_code="US", count=noOfVideos)  # get the videos object
    d = video_by_chart
    videos = {}                 # map for video ID and title
    for item in d.items:                # populate the map
        videos[item.to_dict()["id"]] = item.to_dict()["snippet"]["title"]
    for video in videos:                # add the videos to database(firebase)
        db.child("videos").child(video).child("title").set(videos[video])


def getVideos():
    """
    Name: Get Videos
    Task: Get all the video links from database and return to the view that called it
    Returns:
        [dict, list]: dict is the map for id and title, list is the list of titles
    """
    data = db.child("videos").get()
    videos = {}
    videoList = []
    for i in data.each():
        videos[i.key()] = i.val()["title"]
        videoList.append(i.val()["title"])
    return videos, videoList


def authUser(email, passw):
    """
    Name: Authenticate User
    Task: To authenticate the user
    Args:
        email ([str]): email of the user
        passw ([str]): password of the user

    Returns:
        [bool]: true if successfully authenticated, else false
    """
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
    except:
        return False
    return True


def checkAdmin(email):
    """
    Name: Check if Admin
    Args:
        email ([str]): email of the user 

    Returns:
        [bool]: returns true if user is admin (checked in firebase) else false
    """
    admins = db.child("superuser").get()
    for s in admins.each():
        if s.val() == email:
            return True
    return False


def deleteVideo(key):
    """
    Name: Delete Video
    Task: To delete the video identified by ID
    Args:
        key ([str]): the ID of the video to be deletes
    """
    db.child("videos").child(key).remove()


def extractId(videoUrl):
    """
    Name: Extract ID from URL
    Task: To extract the ID of the video from  given URL 
    Args:
        videoUrl ([str]): this is the complete url of the youtube video

    Returns:
        [bool]: returns true if success else false
    """
    query = urlparse(videoUrl)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return False


def addVideo(videoUrl):
    """
    Name: Add Video
    Task: Add a new video to the database(firebase)
    Args:
        videoUrl ([str]): url of the video to be added

    Returns:
        [bool]: returns true if url is valid, else false
    """
    videoId = extractId(videoUrl)
    if videoId == None:
        return False
    videoTitle = api.get_video_by_id(video_id=videoId).items[0].to_dict()[
        "snippet"]["title"]
    db.child("videos").child(videoId).child("title").set(videoTitle)
    return True


def setTitle(key, newTitle):
    """
    Name: Set Title
    Task: To change the title of a video
    Args:
        key ([str]): unique id of the video
        newTitle ([str]): new value of the title
    """
    db.child("videos").child(key).child("title").set(newTitle)


def getDescription(key):
    """
    Name: Get Description
    Task: To get the description of the video
    Args:
        key ([str]): unique ID of the video
    """
    return(api.get_video_by_id(
        video_id="CvTApw9X8aA").items[0].to_dict()["snippet"]["description"])


def getComments(key):
    """
    Name: Get Comments
    Task: To get all the comments on a video
    Args:
        key ([str]): unique ID of the video

    Returns:
        [List]: a list of all the comments on the video
    """
    comments = []
    data = db.child("videos").child(key).child(
        "comments").get()    # get comments
    try:
        for i in data.each():
            comments.append(i.val())        # add to comments list
    except:
        return []
    return comments


def setComment(key, comment):
    """
    Name: Set Comment
    Task: To add a new comment to a video
    Args:
        key ([str]): unique ID of the video
        comment ([str]): new comment to be added
    """
    db.child("videos").child(key).child("comments").push(comment)
