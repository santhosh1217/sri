from os import link
from datetime import datetime
import re
from django.http import HttpResponse
from django.shortcuts import redirect, render
from attendance import models
from django.contrib import messages
import random

# email
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
# import cv2
# import numpy
# from pyzbar.pyzbar import decode
###############################################    AUTH     #########################################
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
################################################# ///////  ####################################



def institute_login(request):
    # if request.user.is_authenticated:
    #     return redirect("il")
    # else:
    #     return render(request,'login.html')
    return render(request,'login.html')

def signup(request):
    return render(request,"institute signup.html")

######################################### sign up form validation #####################################################

def submit(request):
    obj =  models.college()
    obj.username = request.POST["username"]
    obj.password = request.POST['password']
    obj.name = request.POST["instituteName"]
    obj.logo = request.FILES.get("logo","game")
    if models.college.objects.filter(username=request.POST["username"]).exists():
             return render(request,"institute signup.html",{"msg":"username exist"})
    else:
        if request.POST['password'] == request.POST['confirmPassword']:

            if models.college.objects.filter(name=request.POST["instituteName"]).exists():
                return render(request,"institute signup.html",{"msg":"institute name already exists"})
            else:
                obj.save()
                return redirect("home")
        else:
            return render(request,"institute signup.html",{"msg":"password not match"})



################################################################# login ############################################################

def login(request):
    if request.method == "POST":
        users = request.POST['username']
        passw = request.POST['password']
        if request.POST["type"] == "admin":
            if models.college.objects.filter(username=users).exists():
                obj = models.college.objects.get(username=users)
                if obj.password == passw:
                            return redirect("staffviewpage1",users)
                    #     return render(request,"staffAdmin.html",{"mydata":data,"logo":obj.logo.url,"userid":obj.username,"name":obj.name,"aid":users})
                    # else:
                    #     print(users)
                    #     return render(request,"staffAdmin.html",{"logo":obj.logo.url,"userid":obj.username,"name":obj.name,"aid":users})

                else:
                    messages.info(request,"2")
                    return redirect("home")

            else:
                messages.info(request,"1")
                return redirect("home")


        else:
            authuser= authenticate(request,username=users,password=passw)
            if authuser is not None:
                auth_login(request,authuser)
                return redirect("home")

#################################################################  LOG OUT ##############################
def logout(request):
    auth_logout(request)
    return redirect('home')
#################################################################   RETURN STAFF VIEW PAGE  #############
def staffviewpage(request,users):
    print(users)
    if models.college.objects.filter(username=users).exists():
            obj = models.college.objects.get(username=users)
            if models.Staff.objects.filter(staffCollege=obj.name).exists():
                data=models.Staff.objects.filter(staffCollege=obj.name)
                return render(request,"staffAdmin.html",{"mydata":data,"logo":obj.logo.url,"userid":obj.username,"name":obj.name,"aid":users})
            else:
                return render(request,"staffAdmin.html",{"logo":obj.logo.url,"userid":obj.username,"name":obj.name,"aid":users})





###################################################################### after login #########
def indexhome(request):
    return render(request,"indexhome.html")

def stafflog(request):
    users=request.user.username
    print(users)
    return redirect("deps",users)
def sd(request):
    users=request.user.username
    print(users)
    return redirect("studetail",users)
def studetail(request,users):
    if  models.Staff.objects.filter(staffUsername=users).exists():
        obj =  models.Staff.objects.get(staffUsername=users)
        stu = models.Student.objects.filter(clg = obj.staffCollege)
        print(stu)
        li = []
        for i in stu:
            print(i.clg)
            dic = {}
            ob = models.Attendance.objects.get(Roll=i.reg)
            print(ob)
            dic["name"] = i.name
            dic["roll"] = i.reg
            dic["dep"] = i.department
            dic["year"] = i.year
            dic["date"] = ob.Date_field
            dic["fn"] = ob.morning_attendance
            if ob.morning_attendance == "True":
                dic["fn_color"] = "green"
            else:
                dic["fn_color"] = "red"

            dic["an"] = ob.afternoon_attendance
            if ob.afternoon_attendance == "True":
                dic["an_color"] = "green"
            else:
                dic["an_color"] = "red"
          

            s = models.Attendance.objects.filter(Roll=i.reg,Date_field=ob.Date_field,College_Name=i.clg,morning_attendance=True)
            t = models.Attendance.objects.filter(Roll=i.reg,Date_field=ob.Date_field,College_Name=i.clg,afternoon_attendance=True)
            lent= len(s)+len(t)
            dic["per"] = lent
            li.append(dic)







        
        return render(request,'studentrecords.html',{"detial":li})

def dep(request,users):
    if  models.Staff.objects.filter(staffUsername=users).exists():
        obj =  models.Staff.objects.get(staffUsername=users)
        obj1 = models.college.objects.get(name = obj.staffCollege)
        return render(request,"department.html",{"name":obj1.name,"logo":obj1.logo.url,"userid":obj.staffUsername})
##############################################################    years #############################################################

def year(request,user,depart):
    stf = models.Staff.objects.get(staffUsername=user)
    obj1 = models.college.objects.get(name=stf.staffCollege)
    print(stf.staffDep)
    print("li "+ depart)
    if stf.staffDep == depart:
        return render(request, "year.html",{"link":depart,"name":stf.staffCollege,"logo":obj1.logo.url,"userid":user})
    else:
        return render(request,"department.html",{"name":obj1.name,"logo":obj1.logo.url,"userid":stf.staffUsername,"msg":"true"})

############################################################## attendance ########################################################
def auto(request,user,department,year):
    print("success!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    l =[]
    staf = models.Staff.objects.get(staffUsername = user)
    clg = models.college.objects.get(name=staf.staffCollege)
    obj = models.Student.objects.all().filter(department=department,year=year,clg=staf.staffCollege)
    for i in obj:
        if request.POST.get(str(i.id),False):
            i.attendance=True

    for i in obj:
        if i.attendance  == False:
            l.append(i.name)   
            number = i.s_mobile   
            msg = request.POST["whatsapp"]
            # msg = "*Greetings from "+clg.name +" :*"+" "+msg
            print(clg.logo.url)
            # recipient_email = request.POST['whatsapp']
            
            send_mail('Test Email', msg, 'your_email@gmail.com', [number])
            print("send")






def department(request,user,department,year):
    obj = models.Staff.objects.get(staffUsername=user)
    obj1 = models.college.objects.get(name=obj.staffCollege)
    student = models.Student.objects.filter(department=department,year=year,clg = obj1.name)
    print(student)
    years = {"1":"first year","2":"second year","3":"third year","4":"final year"}
    today=datetime.today()
    f_date=today.strftime("%d-%m-%Y")
    # Att=models.Attendance.objects.filter(obj1.name,Date_field=f_date)
    message = {"department":department,"year": years.get(str(year)),"logo":obj1.logo.url,"name":obj1.name,"detial":student,"userid":user}
    print(obj1.name + department + year + f_date)
    
    if models.Register.objects.filter(cname = obj1.name , dep = department,year = year,date = f_date).exists():
        data = models.Register.objects.get(cname = obj1.name , dep = department,year = year,date = f_date)
        print(data.fnattnd)
        if data.fnattnd or data.anattnd:
            new = []
            for s in student:
                print(s.name)
                atd = models.Attendance.objects.get(College_Name=obj1.name,Date_field = f_date,Roll = s.reg)
                dic = {}
                dic["name"] = s.name
                dic["reg"] = s.reg
                dic["id"] = s.id
                
               	if atd.morning_attendance == "True":
                    dic["fn"] = atd.morning_attendance

                
        
               	if atd.afternoon_attendance == "True":
                    dic["an"]  = atd.afternoon_attendance


               	new.append(dic)
            
            print(new)
            message = {"department":department,"year": years.get(str(year)),"logo":obj1.logo.url,"name":obj1.name,"detial":new,"userid":user}
            if data.fnattnd:
                message["msg1"]="apple"
            if data.anattnd:
                message["msg2"]="orange"
            return render(request,"attendance.html",message,)


        # elif data.fnattnd:
        #     new = []
        #     for s in student:
        #         print(s.name)
        #         atd = models.Attendance.objects.get(College_Name=obj1.name,Date_field = f_date,Roll = s.reg)
        #         dic = {}
        #         dic["name"] = s.name
        #         dic["reg"] = s.reg
                
        #        	if atd.morning_attendance == "True":
        #             dic["fn"] = atd.morning_attendance

        #        	new.append(dic)
        #     message = {"department":department,"year": years.get(str(year)),"logo":obj1.logo.url,"name":obj1.name,"detial":new,"userid":user,"msg":"submited"}
        #     return render(request,"attendance.html",message,)
        # else:
        #     return render(request,"attendance.html",message,)
    

    else:
        print("hello")
        return render(request,"attendance.html",message,)

                                        # # # ' ' 'STAFF ' ' ' # # #

############################################################ ADD STAFF ################################################################

def addstaffs(request,users):
    url=request.get_full_path()
    data=models.Staff.objects.all()
    obj=models.Staff()
    if request.method=='POST':

        staffUsername = request.POST["s_username"]
        staffPassword= request.POST["s_password"]
        staffName = request.POST["s_name"]
        obj.staffName = request.POST["s_name"]
        obj.staffDep = request.POST["s_dep"]
        obj.staffPosition = request.POST["s_position"]
        obj.staffUsername = request.POST["s_username"]
        obj.staffPassword= request.POST["s_password"]
        obj1 = models.college.objects.get(username=users)
        obj.staffCollege = obj1.name
        obj.save()
        ####
        user = User.objects.create_user(username=staffUsername,password=staffPassword,email="")
        User.first_name=staffName
        user.is_staff=True
        user.is_superuser=True
        user.save()
        return redirect("staffviewpage1",users)
########################################################### NEW STAFF ##########################################
def newstaff(request,users):
    return render(request,"staffRegister.html")

########################################################### UPDATE ###################################################################

def staff_update(request,id,users):
    if request.method == "POST":

        obj=models.Staff.objects.get(id=id)
        obj.staffName = request.POST["s_name"]
        obj.staffDep = request.POST["s_dep"]
        obj.staffPosition = request.POST["s_position"]
        obj.staffUsername = request.POST["s_username"]
        obj.staffPassword= request.POST["s_password"]
        obj.save()
        return redirect("staffviewpage1",users)

    else:

        obj=models.Staff.objects.get(id=id)
        return render(request,"staffUpdate.html",{"data":obj})


########################################################## DELETE ###################################################################

def staff_delete(request,id,users):
    print("deleted")
    url=request.get_full_path()
    mydata=models.Staff.objects.get(id=id)
    mydata.delete()
    return redirect("staffviewpage1",users)


                                             # # # " " " STUDENT " " " # # #


##############################################################  ADMIN  ###############################################

def admin(request,user,department,year):
    obj = models.Staff.objects.get(staffUsername=user)
    obj1 = models.college.objects.get(name=obj.staffCollege)
    detial = models.Student.objects.filter(department=department,year=year,clg = obj1.name)
    return render(request,"studentAdmin.html",{"logo":obj1.logo.url,"mydata":detial,"userid":obj.staffUsername,"name":obj1.name})
############################################################ UPDATE   ###############################################

def update(request,id,user,department,year):
    if request.method=='POST':
        obj = models.Student.objects.get(id=id)
        obj.name = request.POST["sname"]
        obj.reg = request.POST["regnum"]
        obj.s_mobile = request.POST["s_number"]
        obj.p_mobile = request.POST["p_number"]
        obj.save()
        return redirect("studentAdmin",user,department,year)
    else:
        obj = models.Student.objects.get(id=id)
        clg = models.college.objects.get(name = obj.clg)
        return render(request,"studentUpdate.html",{"data":obj,"logo":clg.logo.url,"name":clg.name,"userid":str(user)})

######################################################### DELETE ##################################################

def delete(request,id,user,department,year):
    obj = models.Student.objects.get(id = id)
    obj.delete()
    return redirect("studentAdmin",user,department,year)

######################################################### ADD STUDENT  ##############################################

def adddata(request,user,department,year):
    obj1 = models.Staff.objects.get(staffUsername=user)
    obj2 = models.Student()
    obj2.name = request.POST["names"]
    obj2.reg = request.POST["r_number"]
    obj2.s_mobile = request.POST["s_number"]
    obj2.p_mobile = request.POST["p_number"]
    obj2.clg = str(obj1.staffCollege)
    obj2.department = str(department)
    obj2.year = str(year)
    obj2.save()
    return redirect("studentAdmin",user,department,year)

def newstudent(request,user,department,year,admin):
    staff = models.Staff.objects.get(staffUsername=user)
    college = models.college.objects.get(name = staff.staffCollege)
    return render(request,"studentRegister.html",{"name":college.name,"logo":college.logo.url,"userid":user,})

def back(request,user,department,year):

    return redirect("attendance",user,department,year)




##########################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   SUBMIT   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@####################
def send(request,user,department,year,val):

    l =[]
    staf = models.Staff.objects.get(staffUsername = user)
    clg = models.college.objects.get(name=staf.staffCollege)
    obj = models.Student.objects.all().filter(department=department,year=year,clg=staf.staffCollege)
    for i in obj:
        if request.POST.get(str(i.id),False):
            i.attendance=True

    for i in obj:
        if i.attendance  == False:
            l.append(i.name)
            number = i.s_mobile
            msg = request.POST["whatsapp"]
            print(number)
            print("*******************************************")
            print(msg)
            # msg = "*Greetings from "+clg.name +" :*"+" "+msg
            print(clg.logo.url)
            send_mail("college", msg, 'your_email@gmail.com', [number])
   
############################################   SEND ATTENDANCE #############################
def send_attendance(request,user,department,year,id):
    obj = models.Staff.objects.get(staffUsername=user)
    detial = models.Student.objects.filter(department=department,year=year,clg = obj.staffCollege)
    obj1 = models.Attendance.objects.all()
    
    today=datetime.today()
    f_date=today.strftime("%d-%m-%Y")
    
    at = models.Register()
    at.cname = obj.staffCollege
    at.dep = department
    at.year = year
    at.date = f_date
    msg = request.POST["whatsapp"]
    if id == 1:
   
        print(111111111111111111111111)
        at.fnattnd = True
        at.save()
        
        for i in detial:
            
            ob=models.Attendance()
            ob.Roll=str(i.reg)
            ob.Date_field=f_date
            if request.POST.get(str(i.reg),False):
                print("wowwwww")
                ob.morning_attendance=True
                
            #sending mail
            if (ob.morning_attendance) == False:
                send_mail("college", msg, 'your_email@gmail.com', [i.s_mobile])
                
            
            ob.College_Name = str(obj.staffCollege)
            ob.save()
    if id == 2:
     
        ob = models.Register.objects.get(cname=obj.staffCollege,dep=department,year=year)
        ob.anattnd = True
        ob.save()
        for i in detial:
            z = models.Attendance.objects.get(Roll = i.reg,Date_field = f_date,College_Name = i.clg)
            if request.POST.get(str(i.name),False):
               
                z.afternoon_attendance=True
            print(str(z.afternoon_attendance)+"PPPPPPPPPPPPPPPPPPPPPPPPP")
            
            #sending mail
            if str(z.afternoon_attendance) == str(False):
                print("absenttttttttttttttttttttttttttttttttttt" + i.name)
                send_mail("college", msg, 'your_email@gmail.com', [i.s_mobile])

            z.save()
                
            
            
        


        
       
        


    return redirect("attendance",user,department,year)
    # student = models.Student.objects.filter(department=department,year=year,clg = obj1.name)
    
