import mysql.connector
import sys
import datetime
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template
from random import randint

app = Flask(__name__)


@app.route('/')
def renderLoginPage():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def verifyAndRenderRespective():
    username = request.form['username']
    password = request.form['password']

    try:

        if username == '1' and password == '1':
            res = runQuery('call delete_old()')
            return render_template('manager.html')
        elif username == '2' and password == '2':
            res = runQuery('call delete_old()')
            return render_template('cashier.html')
        elif username == '3' and password == '3':
            res = runQuery('call delete_old()')
            return render_template('director.html')
        else:
            res = runQuery(
                "SELECT staff_id,staff_name,citizen_id,position FROM staffs WHERE staff_name = '"+username+"' and citizen_id = '"+password+"'")

            staffs = []
            for i in res:
                staffs.append([i[0], i[1], i[2], i[3]])
            if i[0] == '':
                return render_template('loginFail.html')
            else:
                if i[3] == 'cashier':
                    res = runQuery('call delete_old()')
                    return render_template('cashier.html', staffs=staffs)
                if i[3] == 'manager':
                    res = runQuery('call delete_old()')
                    return render_template('manager.html')
                if i[3] == 'director':
                    res = runQuery('call delete_old()')
                    return render_template('director.html')

    except Exception as e:
        print(e)
        return render_template('loginFail.html')


# Routes for cashier
@app.route('/getMoviesShowingOnDate', methods=['POST'])
def moviesOnDate():
    date = request.form['date']

    res = runQuery(
        "SELECT DISTINCT movie_id,movie_name,type FROM movies NATURAL JOIN shows WHERE Date = '"+date+"'")

    if res == []:
        return '<h4>No Movies Showing</h4>'
    else:
        return render_template('movies.html', movies=res)


@app.route('/getTimings', methods=['POST'])
def timingsForMovie():
    date = request.form['date']
    movieID = request.form['movieID']
    movieType = request.form['type']

    res = runQuery("SELECT time FROM shows WHERE Date='"+date +
                   "' and movie_id = "+movieID+" and type ='"+movieType+"'")

    list = []

    for i in res:
        list.append((i[0], int(i[0]/100), i[0] %
                    100 if i[0] % 100 != 0 else '00'))

    return render_template('timings.html', timings=list)


@app.route('/getShowID', methods=['POST'])
def getShowID():
    date = request.form['date']
    movieID = request.form['movieID']
    movieType = request.form['type']
    time = request.form['time']

    res = runQuery("SELECT show_id FROM shows WHERE Date='"+date +
                   "' and movie_id = "+movieID+" and type ='"+movieType+"' and time = "+time)
    return jsonify({"showID": res[0][0]})


@app.route('/getAvailableSeats', methods=['POST'])
def getSeating():
    showID = request.form['showID']

    res = runQuery(
        "SELECT class,no_of_seats FROM shows NATURAL JOIN halls WHERE show_id = "+showID)

    totalGold = 0
    totalStandard = 0

    for i in res:
        if i[0] == 'gold':
            totalGold = i[1]
        if i[0] == 'standard':
            totalStandard = i[1]

    res = runQuery(
        "SELECT seat_no FROM booked_tickets WHERE show_id = "+showID)

    goldSeats = []
    standardSeats = []

    for i in range(1, totalGold + 1):
        goldSeats.append([i, ''])

    for i in range(1, totalStandard + 1):
        standardSeats.append([i, ''])

    for i in res:
        if i[0] > 1000:
            goldSeats[i[0] % 1000 - 1][1] = 'disabled'
        else:
            standardSeats[i[0] - 1][1] = 'disabled'

    return render_template('seating.html', goldSeats=goldSeats, standardSeats=standardSeats)


@app.route('/getPrice', methods=['POST'])
def getPriceForClass():
    showID = request.form['showID']
    seatClass = request.form['seatClass']

    res = runQuery("INSERT INTO halls VALUES(-1,'-1',-1)")

    res = runQuery("DELETE FROM halls WHERE hall_id = -1")

    res = runQuery(
        "SELECT price FROM shows NATURAL JOIN price_listing WHERE show_id = "+showID)

    if res == []:
        return '<h5>Prices Have Not Been Assigned To This Show, Try Again Later</h5>'

    price = int(res[0][0])
    if seatClass == 'gold':
        price = price * 1.5

    return '<h5>Ticket Price: '+str(price)+' VND</h5>\
	<button onclick="confirmBooking()">Confirm</button>'


@app.route('/insertBooking', methods=['POST'])
def createBooking():
    showID = request.form['showID']
    staffID = request.form['staffID']
    seatNo = request.form['seatNo']
    seatClass = request.form['seatClass']

    if seatClass == 'gold':
        seatNo = int(seatNo) + 1000

    ticketNo = 0
    res = None

    while res != []:
        ticketNo = randint(0, 2147483646)
        res = runQuery(
            "SELECT ticket_no FROM booked_tickets WHERE ticket_no = "+str(ticketNo))
    res = runQuery(
        "INSERT INTO booked_tickets VALUE("
        + str(ticketNo)+","
        + showID+","
        + str(seatNo)+","
        + staffID+")"
    )

    if res == []:
        return '<h5>Ticket Successfully Booked</h5>\
		<h6>Ticket Number: '+str(ticketNo)+'</h6>'


# Routes for manager
# Route for movies
@app.route('/getMovieOption', methods=['POST'])
def getMovieOption():
    return render_template('moviesOption.html')

# Add movie route


@app.route('/fetchMovieInsertForm', methods=['GET'])
def getMovieForm():
    return render_template('movieForm.html')


@app.route('/insertMovie', methods=['POST'])
def insertMovie():
    movieName = request.form['movieName']
    movieLen = request.form['movieLen']
    movieLang = request.form['movieLang']
    types = request.form['types']
    startShowing = request.form['startShowing']
    endShowing = request.form['endShowing']
    res = runQuery('SELECT * FROM movies')

    for i in res:
        if i[1] == movieName and i[2] == int(movieLen) and i[3] == movieLang \
                and i[4].strftime('%Y/%m/%d') == startShowing and i[5].strftime('%Y/%m/%d') == endShowing:
            return '<h5>The Exact Same Movie Already Exists</h5>'

    movieID = 0
    res = None

    while res != []:
        movieID = randint(0, 2147483646)
        res = runQuery(
            "SELECT movie_id FROM movies WHERE movie_id = "+str(movieID))

    res = runQuery("INSERT INTO movies VALUES("+str(movieID)+",'"+movieName+"',"+movieLen +
                   ",'"+movieLang+"','"+startShowing+"','"+endShowing+"')")

    if res == []:
        print("Was able to add movie")
        subTypes = types.split(' ')

        while len(subTypes) < 3:
            subTypes.append('NUL')

        res = runQuery("INSERT INTO types VALUES("+str(movieID) +
                       ",'"+subTypes[0]+"','"+subTypes[1]+"','"+subTypes[2]+"')")

        if res == []:
            return '<h5>Movie Successfully Added</h5>\
			<h6>Movie ID: '+str(movieID)+'</h6>'
        else:
            print(res)
    else:
        print(res)

    return '<h5>Something Went Wrong</h5>'

# Update movie route


@app.route('/getMovieInfo', methods=['GET'])
def movieList():
    res = runQuery("SELECT * FROM movies")

    return render_template('currentMovieForUpdate.html', movies=res)


@app.route('/setNewMovieInfo', methods=['POST'])
def setMovieInfo():
    movieID = request.form['movieID']
    newMovieName = request.form['newMovieName']
    newMovieLen = request.form['newMovieLen']
    newMovieLanguage = request.form['newMovieLanguage']
    types = request.form['types']
    startShowing = request.form['startShowing']
    endShowing = request.form['endShowing']
    res = runQuery("UPDATE movies SET movie_name = '"+newMovieName+"', length = "+str(newMovieLen)+", language = '" +
                   newMovieLanguage+"',  show_start = '"+startShowing+"', show_end = '"+endShowing+"' WHERE movie_id = "+str(movieID))

    if res == []:
        subTypes = types.split(' ')
        while len(subTypes) < 3:
            subTypes.append('NUL')
        res = runQuery("UPDATE types SET type1 = '"+subTypes[0]+"', type2 = '" +
                       subTypes[1]+"', type3 = '"+subTypes[2]+"' WHERE movie_id = " + str(movieID))
        if res == []:
            return '<h5>Movie Info Successfully Changed</h5>'
        else:
            print(res)
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'
# delete movie route


@app.route('/getMovieInfoForDelete', methods=['GET'])
def movieList1():
    res = runQuery("SELECT * FROM movies")
    return render_template('currentMovieForDelete.html', movies=res)


@app.route('/deleteMovieInfo', methods=['POST'])
def deleteMovieInfo():
    movieID = request.form['movieID']
    res = runQuery("DELETE FROM movies WHERE movie_id = "+str(movieID))
    if res == []:
        return '<h5>Info Successfully Deleted</h5>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'
# Search movie route


@app.route('/searchMovieInfo', methods=['POST'])
def searchMovieInfo():
    searchMovieName = request.form['searchMovieName']
    res = runQuery(
        "SELECT * FROM movies WHERE movie_name = '"+searchMovieName+"'")
    if res == []:
        return '<h4>No Movie Info</h4>'

    return render_template('searchMovieInfo.html', movies=res)

# Schedule A Show


@app.route('/getValidMovies', methods=['POST'])
def validMovies():
    showDate = request.form['showDate']

    res = runQuery("SELECT movie_id,movie_name,length,language FROM movies WHERE show_start <= '"+showDate +
                   "' and show_end >= '"+showDate+"'")
    if res == []:
        return '<h5>No Movies Available for Showing On Selected Date</h5>'
    movies = []
    for i in res:
        subTypes = runQuery("SELECT * FROM types WHERE movie_id = "+str(i[0]))

        t = subTypes[0][1]

        if subTypes[0][2] != 'NUL':
            t = t + ' ' + subTypes[0][2]
        if subTypes[0][3] != 'NUL':
            t = t + ' ' + subTypes[0][3]
        movies.append((i[0], i[1], t, i[2], i[3]))

    return render_template('validMovies.html', movies=movies)


@app.route('/getHallsAvailable', methods=['POST'])
def getHalls():
    movieID = request.form['movieID']
    showDate = request.form['showDate']
    showTime = request.form['showTime']
    res = runQuery("SELECT length FROM movies WHERE movie_id = "+movieID)
    movieLen = res[0][0]
    showTime = int(showTime)
    showTime = int(showTime / 100)*60 + (showTime % 100)
    endTime = showTime + movieLen
    res = runQuery(
        "SELECT hall_id, length, time FROM shows NATURAL JOIN movies WHERE Date = '"+showDate+"'")
    unavailableHalls = set()
    for i in res:
        x = int(i[2] / 100)*60 + (i[2] % 100)
        y = x + i[1]
        if x >= showTime and x <= endTime:
            unavailableHalls = unavailableHalls.union({i[0]})
        if y >= showTime and y <= endTime:
            unavailableHalls = unavailableHalls.union({i[0]})
    res = runQuery("SELECT DISTINCT hall_id FROM halls")
    availableHalls = set()
    for i in res:
        availableHalls = availableHalls.union({i[0]})
    availableHalls = availableHalls.difference(unavailableHalls)
    if availableHalls == set():
        return '<h5>No Halls Available On Given Date And Time</h5>'

    return render_template('availableHalls.html', halls=availableHalls)


@app.route('/insertShow', methods=['POST'])
def insertShow():
    hallID = request.form['hallID']
    movieID = request.form['movieID']
    movieType = request.form['movieType']
    showDate = request.form['showDate']
    showTime = request.form['showTime']
    showID = 0
    res = None
    while res != []:
        showID = randint(0, 2147483646)
        res = runQuery(
            "SELECT show_id FROM shows WHERE show_id = "+str(showID))
    res = runQuery("INSERT INTO shows VALUES("+str(showID)+","+movieID+","+hallID +
                   ",'"+movieType+"',"+showTime+",'"+showDate+"',"+'NULL'+")")
    print(res)
    if res == []:
        return '<h5>Show Successfully Scheduled</h5>\
		<h6>Show ID: '+str(showID)+'</h6>'
    else:
        print(res)

    return '<h5>Something Went Wrong</h5>'

# Alter Price


@app.route('/getPriceList', methods=['GET'])
def priceList():
    res = runQuery("SELECT * FROM price_listing ORDER BY type")
    sortedDays = ['Sunday', 'Monday', 'Tuesday',
                  'Wednesday', 'Thursday', 'Friday', 'Saturday']
    res = sorted(res, key=lambda x: sortedDays.index(x[2]))

    return render_template('currentPrices.html', prices=res)


@app.route('/setNewPrice', methods=['POST'])
def setPrice():
    priceID = request.form['priceID']
    newPrice = request.form['newPrice']
    res = runQuery("UPDATE price_listing SET price = " +
                   str(newPrice)+" WHERE price_id = "+str(priceID))
    if res == []:
        return '<h5>Price Successfully Changed</h5>\
			<h6>Standard: '+newPrice+' VND</h6>\
			<h6>Gold: '+str(int(int(newPrice) * 1.5))+' VND</h6>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Route cho member
# Add member route


@app.route('/getMemberOption', methods=['POST'])
def getMemberOption():
    return render_template('memberOption.html')


@app.route('/fectchMemberInsertForm', methods=['GET'])
def getMemberForm():
    return render_template('memberForm.html')


@app.route('/InsertMember', methods=['POST'])
def insertMember():
    memberName = request.form['memberName']
    memberDob = request.form['memberDob']
    memberGender = request.form['memberGender']
    memberIDcard = request.form['memberIDcard']
    memberPhoneNumber = request.form['memberPhoneNumber']
    memberEmail = request.form['memberEmail']
    memberType = request.form['memberType']
    res = runQuery('SELECT * FROM members')
    for i in res:
        if i[1] == memberName and i[4] == memberIDcard:
            return '<h5>The Member Info Already Exists</h5>'
    memberID = 0
    res = None
    while res != []:
        memberID = randint(0, 2147483646)
        res = runQuery(
            "SELECT member_id FROM members WHERE member_id = "+str(memberID))
    res = runQuery("INSERT INTO members VALUES("+str(memberID)+",'"+memberName+"','"+memberDob +
                   "','"+memberGender+"',"+str(memberIDcard)+","+str(memberPhoneNumber)+",'"+memberEmail+"','"+memberType+"')")
    if res == []:
        print("Was able to add member")
        if res == []:
            return '<h5>Member Successfully Added</h5>\
			<h6>Member ID: '+str(memberID)+'</h6>'
        else:
            print(res)
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Update member route


@app.route('/getMemberInfo', methods=['GET'])
def memberList():
    res = runQuery("SELECT * FROM members")
    return render_template('currentMemberForUpdate.html', members=res)


@app.route('/setNewMemberInfo', methods=['POST'])
def setMemberInfo():
    memberID = request.form['memberID']
    newMemberName = request.form['newMemberName']
    newMemberDob = request.form['newMemberDob']
    newMemberGender = request.form['newMemberGender']
    newMemberIDcard = request.form['newMemberIDcard']
    newMemberPhoneNumber = request.form['newMemberPhoneNumber']
    newMemberEmail = request.form['newMemberEmail']
    newMemberType = request.form['newMemberType']
    res = runQuery("UPDATE members SET member_name = '"+newMemberName+"', date_of_birth = '"+newMemberDob+"', gender = '"+newMemberGender+"', citizen_id = " +
                   str(newMemberIDcard)+", phone_number = "+str(newMemberPhoneNumber)+", email = '"+newMemberEmail+"', member_type = '"+newMemberType+"' WHERE member_id = "+str(memberID))

    if res == []:
        return '<h5>Info Successfully Changed</h5>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Delete member route


@app.route('/getMemberInfoForDelete', methods=['GET'])
def memberList1():
    res = runQuery("SELECT * FROM members")
    return render_template('currentMemberForDelete.html', members=res)


@app.route('/deleteMemberInfo', methods=['POST'])
def deleteMemberInfo():
    memberID = request.form['memberID']
    res = runQuery(
        "DELETE FROM members WHERE member_id = "+str(memberID))
    if res == []:
        return '<h5>Info Successfully Deleted</h5>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Show member route


@app.route('/getMemberInfo1', methods=['GET'])
def memberList2():
    res = runQuery("SELECT * FROM members")
    return render_template('currentMemberForShowInfo.html', members=res)


@app.route('/showSelectedMemberInfo', methods=['POST'])
def showSelectedMemberInfo():
    memberID = request.form['memberID']
    res = runQuery(
        "SELECT member_id,member_name,date_of_birth,phone_number,email,member_type FROM members WHERE member_id="+str(memberID))
    members = []
    for i in res:
        members.append([i[0], i[1], i[2], i[3], i[4], i[5]])
    return render_template('showMemberInfo.html', members=members)


# Search member route
@app.route('/searchMemberInfo', methods=['POST'])
def searchMemberInfo():
    searchMemberName = request.form['searchMemberName']
    res = runQuery(
        "SELECT * FROM members WHERE member_name = '"+searchMemberName+"'")
    if res == []:
        return '<h4>No Member Info</h4>'
    return render_template('searchMemberInfo.html', members=res)


# ROUTE FOR DIRECTOR
# Staff options
# Add staff route
@app.route('/getStaffOption', methods=['POST'])
def getStaffOption():
    return render_template('staffOption.html')


@app.route('/fectchStaffInsertForm', methods=['GET'])
def getStaffForm():
    return render_template('staffForm.html')


@app.route('/InsertStaff', methods=['POST'])
def insertStaff():
    staffName = request.form['staffName']
    staffDob = request.form['staffDob']
    staffGender = request.form['staffGender']
    staffIDcard = request.form['staffIDcard']
    staffPhoneNumber = request.form['staffPhoneNumber']
    staffEmail = request.form['staffEmail']
    staffAddress = request.form['staffAddress']
    staffPosition = request.form['staffPosition']
    staffSalary = request.form['staffSalary']
    res = runQuery('SELECT * FROM staffs')
    for i in res:
        if i[1] == staffName and i[4] == staffIDcard:
            return '<h5>The Staff Info Already Exists</h5>'
    staffID = 0
    res = None
    while res != []:
        staffID = randint(0, 2147483646)
        res = runQuery(
            "SELECT staff_id FROM staffs WHERE staff_id = "+str(staffID))

    res = runQuery("INSERT INTO staffs VALUES("+str(staffID)+",'"+staffName+"','"+staffDob +
                   "','"+staffGender+"',"+str(staffIDcard)+",'"+staffPosition+"',"+str(staffPhoneNumber)+",'"+staffEmail+"','"+staffAddress+"','"+staffSalary+"')")

    if res == []:
        print("Was able to add staff")
        if res == []:
            return '<h5>Staff Successfully Added</h5>\
			<h6>Staff ID: '+str(staffID)+'</h6>'
        else:
            print(res)
    else:
        print(res)

    return '<h5>Something Went Wrong</h5>'

# Update staff route


@app.route('/getStaffInfo', methods=['GET'])
def staffList():
    res = runQuery("SELECT * FROM staffs")
    return render_template('currentStaffForUpdate.html', staffs=res)


@app.route('/setNewStaffInfo', methods=['POST'])
def setStaffInfo():
    staffID = request.form['staffID']
    newStaffName = request.form['newStaffName']
    newStaffDob = request.form['newStaffDob']
    newStaffGender = request.form['newStaffGender']
    newStaffIDcard = request.form['newStaffIDcard']
    newStaffPhoneNumber = request.form['newStaffPhoneNumber']
    newStaffEmail = request.form['newStaffEmail']
    newStaffAddress = request.form['newStaffAddress']
    newStaffPosition = request.form['newStaffPosition']
    newStaffSalary = request.form['newStaffSalary']
    res = runQuery("UPDATE staffs SET staff_name = '"+newStaffName+"', date_of_birth = '"+newStaffDob+"', gender = '"+newStaffGender+"', citizen_id = " +
                   str(newStaffIDcard)+", position = '"+newStaffPosition+"', phone_number = "+str(newStaffPhoneNumber)+", email = '"+newStaffEmail+"', staff_address = '"+newStaffAddress+"', staff_salary = '"+newStaffSalary+"' WHERE staff_id = "+str(staffID))

    if res == []:
        return '<h5>Info Successfully Changed</h5>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Delete staff route


@app.route('/getStaffInfoForDelete', methods=['GET'])
def staffList1():
    res = runQuery("SELECT * FROM staffs")
    return render_template('currentStaffForDelete.html', staffs=res)


@app.route('/deleteStaffInfo', methods=['POST'])
def deleteStaffInfo():
    staffID = request.form['staffID']
    res = runQuery("DELETE FROM staffs WHERE staff_id = "+str(staffID))
    if res == []:
        return '<h5>Info Successfully Deleted</h5>'
    else:
        print(res)
    return '<h5>Something Went Wrong</h5>'

# Show staff route


@app.route('/getStaffInfo1', methods=['GET'])
def staffList2():
    res = runQuery("SELECT * FROM staffs")
    return render_template('currentStaffForShowInfo.html', staffs=res)


@app.route('/showSelectedStaffInfo', methods=['POST'])
def showSelectedStaffInfo():
    staffID = request.form['staffID']
    res = runQuery(
        "SELECT staff_id,staff_name,date_of_birth,phone_number,email,staff_address,position,staff_salary FROM staffs WHERE staff_id="+str(staffID))
    staffs = []
    for i in res:
        staffs.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]])
    return render_template('showStaffInfo.html', staffs=staffs)

# Search staff route


@app.route('/searchStaffInfo', methods=['POST'])
def searchStaffInfo():
    searchStaffName = request.form['searchStaffName']
    res = runQuery(
        "SELECT * FROM staffs WHERE staff_name = '"+searchStaffName+"'")
    if res == []:
        return '<h4>No Staff Info</h4>'
    return render_template('searchStaffInfo.html', staffs=res)

# Revenue movie route


@app.route('/getMovieInfoForRevenue', methods=['GET'])
def movieListForRevenue():
    res = runQuery("SELECT * FROM movies")
    return render_template('movieForRevenue.html', movies=res)


@app.route('/showMovieRevenue', methods=['POST'])
def showMovieRevenue():
    movieID = request.form['movieID']
    show_res = runQuery(
        "SELECT show_ID FROM shows WHERE movie_ID="+str(movieID)
    )
    if show_res == []:
        return '<h5>This Movie Has No Show Yet</h5>'
    else:
        totalRevenue = 0
        for i in show_res:
            ticket_res = runQuery(
                "SELECT ticket_no,seat_no FROM booked_tickets WHERE show_id = "+str(i[0])+" order by seat_no")
            if ticket_res == []:
                price = 0
            else:
                revenue_res = runQuery(
                    "SELECT price FROM shows NATURAL JOIN price_listing WHERE show_id = "+str(i[0]))
                if revenue_res == []:
                    price = 0
                else:
                    price = int(revenue_res[0][0])
                    for i in ticket_res:
                        if i[1] > 1000:
                            totalRevenue = totalRevenue + price * 1.5
                        else:
                            totalRevenue = totalRevenue + price
    return '<h5>Total Revenue of this movie :'+str(totalRevenue)+' VND</h5>'

# View booked ticket and revenue for each show


@app.route('/getShowsShowingOnDate', methods=['POST'])
def getShowsOnDate():
    date = request.form['date']
    res = runQuery(
        "SELECT show_id,movie_name,type,time FROM shows NATURAL JOIN movies WHERE Date = '"+date+"'")
    if res == []:
        return '<h4>No Shows Showing</h4>'
    else:
        shows = []
        for i in res:
            x = i[3] % 100
            if i[3] % 100 == 0:
                x = '00'
            shows.append([i[0], i[1], i[2], int(i[3] / 100), x])

        return render_template('shows.html', shows=shows)


@app.route('/getBookedWithShowID', methods=['POST'])
def getBookedTickets():
    showID = request.form['showID']

    res = runQuery(
        "SELECT ticket_no,seat_no FROM booked_tickets WHERE show_id = "+showID+" order by seat_no")

    if res == []:
        return '<h5>No Bookings</h5>'

    tickets = []
    for i in res:
        if i[1] > 1000:
            tickets.append([i[0], i[1] - 1000, 'Gold'])
        else:
            tickets.append([i[0], i[1], 'Standard'])

    revenue_res = runQuery(
        "SELECT price FROM shows NATURAL JOIN price_listing WHERE show_id = "+showID)

    if revenue_res == []:
        return '<h5>Can Not Calculate Total Revenue On Show, Try Again Later</h5>'

    revenue = 0
    price = int(revenue_res[0][0])
    for i in res:
        if i[1] > 1000:
            revenue = revenue + price * 1.5
        else:
            revenue = revenue + price

    return render_template('bookedTickets.html', tickets=tickets, revenue=revenue)


# Route sql connection
def runQuery(query):
    try:
        db = mysql.connector.connect(
            host='localhost',
            database='db_theatre1',
            user='root',
            password='123456')

        if db.is_connected():
            print("Connected to MySQL, running query: ", query)
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            res = None
            try:
                res = cursor.fetchall()
            except Exception as e:
                print("Query returned nothing, ", e)
                return []
            return res

    except Exception as e:
        print(e)
        return e

    finally:
        db.close()

    print("Couldn't connect to MySQL")
    # Couldn't connect to MySQL
    return None


if __name__ == "__main__":
    app.run(host='0.0.0.0')
