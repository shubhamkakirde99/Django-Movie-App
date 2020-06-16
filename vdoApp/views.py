from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import auth
from vdoApp.utils import helperFuncs
from django.contrib import messages


def loginPage(request):
    """
    (anyone)
    Name: Login Page
    Task: Render the first home page for the site

    loginPage.html is the html source file for the login page
    """
    return render(request, "loginPage.html")    # Render the home page


def login(request):
    """
    (anyone)
    Name: Login
    Task: (To handle login) Authenticate a user based on the data in the database(firebase)

    Flow: If authenticated successfully, redirected to movies list page, else page reloads

    email, passw obtained from loginPage.html through POST 
    part of email before @ is the username

    user logged in and admin status are put into sessions so that other views can access as required
    """
    message = None
    email = request.POST.get('email')       # get email and passw using POST
    passw = request.POST.get("pass")
    # authenticate user based on firebase data
    authValue = helperFuncs.authUser(email, passw)
    if authValue == False:                          # if authentication fails, prompt invalid creds
        message = "invalid credentials"
        return render(request, "loginPage.html", {"errMsg": message})

    # on authorization, put status as logged in
    request.session["loggedIn"] = True
    username = email.split("@")[0]          # set username using email id
    request.session["username"] = username

    # check if user is admin based on firebase data
    isAdmin = helperFuncs.checkAdmin(email)
    if isAdmin == True:
        request.session["admin"] = True         # if admin, set admin as true
    else:
        request.session["admin"] = False
    # redirect to list of available movies page
    return redirect("/movieList/")


def logout(request):
    """
    (user)
    Name: Logout
    Task: (To handle logout) Clear the session object

    Flow: Clear the session object and redirect to login page
    """
    auth.logout(request)
    request.session = {}                # clear session object
    return render(request, "loginPage.html")


def movieList(request):
    """
    (user)
    Name: Movie List
    Task: (To display list of movies) admins and non admins will see their respective options only

    Flow: If authenticated successfully, user will see a list of movies and stream now option. Admins will see extra options.

    List of movies(name and ID) is obtained from firebase and displayed in a grid

    edit delete and add options are only for admins
    """

    # check if admin to show different options
    isAdmin = request.session["admin"]
    if request.session["loggedIn"] == False:    # if not logged in, redirect to login
        return redirect("/")

    # get videos and IDs from firebase
    videoDict, videoNames = helperFuncs.getVideos()
    # put the video data into session variable
    request.session["videoData"] = videoDict
    return render(request, "movieList.html", {"videos": videoDict, "username": request.session["username"], "admin": isAdmin})


def movie(request, key):
    """
    (user)
    Name: Movie
    Task: (To display movie and comments) this page will have a movie player and comments section

    Flow: The user can play the movie (fullscreen also available) and publically comment

    email, passw obtained from loginPage.html through POST 
    part of email before @ is the username

    user logged in and admin status are put into sessions so that other views can access as required
    """

    isAdmin = request.session["admin"]          # check admin status
    if request.session["loggedIn"] == False:    # if not logged in, redirect to login
        return redirect("/")
    # get the movie name from session
    movieName = request.session["videoData"][key]
    # retrive comments from firebase
    comments = helperFuncs.getComments(key)
    return render(request, "movie.html", {"key": key, "mName": movieName, "username": request.session["username"], "url": helperFuncs.baseUrl+key, "admin": isAdmin, "comments": comments})


def deleteMovie(request, key):
    """
    (admin)
    Name: Delete Movie
    Task: (To delete a movie) Admins can delete any movie

    Flow: If authorized as admin, delete buttons will be visible, deletes from database(firebase)

    """
    # if not authorized or authenticated, do it
    if request.session["admin"] == False or request.session["loggedIn"] == False:
        return redirect("/movieList/")
    # delete the video based on the key from firebase
    helperFuncs.deleteVideo(key)
    return redirect("/movieList/")


def addVideo(request):
    """
    (admin)
    Name: Add Movie
    Task: (To add a movie) Admins can add any movie

    Flow: If authorized as admin, add option will be visible, adds to the database(firebase)

    First, the url is verified to be correct using the youtube API and then the key and title is added to firebase
    """
    isAdmin = request.session["admin"]
    # if not authorized or authenticated, do it
    if request.session["admin"] == False or request.session["loggedIn"] == False:
        return redirect("/movieList/")
    # get the movie URL from the page
    movieUrl = request.POST.get('movieUrl')
    try:
        # if the url is valid, add it
        res = helperFuncs.addVideo(movieUrl)
        messages.info(request, "The movie has been added successfully!")
    except:
        # else prompt to correct it
        messages.error(request, "Please enter a valid URL")
    return redirect("/movieList/")


def editTitle(request, key):
    """
    (admin)
    Name: Edit Title 
    Task: (To edit title of a movie) Admins can edit title of any movie

    Flow: If authorized as admin, add buttons will be visible, changes made to the database(firebase)

    If user is authenticated and authorized, make the changes to database
    """
    isAdmin = request.session["admin"]
    # if not authorized or authenticated, do it
    if request.session["admin"] == False or request.session["loggedIn"] == False:
        return redirect("/movieList/")
    newTitle = request.POST.get("newTitle")     # get new title using POST
    helperFuncs.setTitle(key, newTitle)         # set the title in database
    return redirect("/movieList/")


def addComment(request, key):
    """
    (user)
    Name: Add Comment
    Task: (To add comments to any movie) all authenticated users can add comments

    Flow: Data is taken through POST and database is updated

    The comments get added to their specific videos based on IDs
    """
    if request.session["loggedIn"] == False:    # if not authenticated, do it
        return redirect("/movie/"+key+"/")
    comment = request.POST.get("comment")       # get comments through POST
    # set comments of the respective video
    helperFuncs.setComment(key, comment)
    return redirect("/movie/"+key+"/")


# API view
def apiMovies(request):
    """
    (user)
    Name: API Movies
    Task: (To send a list of available movies) using Rest API

    Flow: Authenticate the user and then send the list of available movies
    """
    email = request.POST.get('email')
    passw = request.POST.get("pass")
    authValue = helperFuncs.authUser(email, passw)  # authenticate the user
    if authValue == False:                          # if unsuccessful, send error
        message = "invalid credentials"
        return JsonResponse({"status": "Login Error"})
    videoDict, videoNames = helperFuncs.getVideos()     # else send movies
    request.session["videoData"] = videoDict
    return JsonResponse({"status": "Success", "videos": videoDict})


# API view
def apiLink(request, key):
    """
    (user)
    Name: API Link
    Task: (To send movie link and description) using Rest API

    Flow: Authenticate the user and then send the link for the requested movie and desc.
    """
    email = request.POST.get('email')
    passw = request.POST.get("pass")
    authValue = helperFuncs.authUser(email, passw)      # authenticate
    if authValue == False:                              # if failed, error
        message = "invalid credentials"
        return JsonResponse({"status": "Login Error"})
    # link = youtube's base link + key
    link = helperFuncs.baseVideoLink+key
    try:
        desc = helperFuncs.getDescription(key)          # get desc.
    except:
        return JsonResponse({"status": "Key Error"})
    data = {"link": link, "desc": desc}                 # final json response
    return JsonResponse({"status": "Success", "data": data})
