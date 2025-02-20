
import Address
import Person
import Customer
import User
#import Admin

Address=Address.Address
Person=Person.Person
Customer=Customer.Customer
User=User.User
#Admin=Admin.Admin

import sqlite3

def createDB():
    db=sqlite3.connect('user.db')
    
    db.execute("""
        CREATE TABLE Address (
            ID INTEGER
            , country TEXT
            , zip TEXT
            , city TEXT
            , street TEXT
            , snumber TEXT
            , PRIMARY KEY(ID))""")

    db.execute("""
        CREATE TABLE Person (
            ID INTEGER
            , name TEXT
            , firstname TEXT
            , email TEXT
            , phone TEXT
            , iban TEXT
            , AddressID INTEGER
            , PRIMARY KEY(ID), FOREIGN KEY(AddressID) REFERENCES Address(ID))""")

    db.execute("""
        CREATE TABLE Customer (
            ID INTEGER
            , company TEXT
            , PersonID INTEGER
            , PRIMARY KEY(ID), FOREIGN KEY(PersonID) REFERENCES Person(ID))""")
    
    db.execute("""
        CREATE TABLE User (
            ID INTEGER
            , username TEXT UNIQUE
            , password TEXT
            , adminrole INTEGER
            , PersonID INTEGER
            , PRIMARY KEY(ID), FOREIGN KEY(PersonID) REFERENCES Person(ID))""")

    db.commit()
    db.close()
    seedroot()
# --- seed root ---
def seedroot():
    adata=['root','root','root','root','root']
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("""INSERT INTO Address (
        country,
        zip,
        city,
        street,
        snumber
        ) VALUES (?, ?, ?, ?, ?);""", adata)
    db.commit()
    db.close()
    
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute(
        "SELECT id FROM Address WHERE zip = ? AND street = ? AND snumber = ?"
        , ('root','root','root'))
    AddressID=cur.fetchone()
    AddressID=AddressID[0]
    pdata=['root','root','root','root','root',AddressID]
    cur.execute("""INSERT INTO Person (
        name,
        firstname,
        email,
        phone,
        iban,
        AddressID
        ) VALUES (?, ?, ?, ?, ?, ?);""", pdata)
    db.commit()
    db.close()
    
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute(
        "SELECT id FROM Person WHERE email = ? AND phone = ? AND iban = ?"
        , ('root','root','root'))
    PersonID=cur.fetchone()
    PersonID=PersonID[0]
    udata=['root','root',1,PersonID]
    cur.execute("""INSERT INTO User (
        username,
        password,
        adminrole,
        PersonID
        ) VALUES (?, ?, ?, ?);""", udata)
    db.commit()
    db.close()
# --- seed ---
def seedAddress(Address):
    data=[Address.getCountry(),Address.getZIP(),Address.getCity(),Address.getStreet(),Address.getSnumber()]
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    try:
        cur.execute("""INSERT INTO Address (
            country,
            zip,
            city,
            street,
            snumber
            ) VALUES (?, ?, ?, ?, ?);""", data)
    except sqlite3.Error as e:
        print(f"an error occurred: {e}")
    db.commit()
    db.close()
    
def seedPerson(Person):
    padata=[Person.getZIP(),Person.getStreet(),Person.getSnumber()]
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute(
        "SELECT id FROM Address WHERE zip = ? AND street = ? AND snumber = ?"
        , (padata))
    AddressID=cur.fetchone()
    if AddressID:
        AddressID=AddressID[0]
        data=[Person.getName(),Person.getFirstname(),Person.getEmail(),Person.getPhone(),Person.getIBAN(),AddressID]
        cur.execute("""INSERT INTO Person (
            name,
            firstname,
            email,
            phone,
            iban,
            AddressID
            ) VALUES (?, ?, ?, ?, ?, ?);""", data)
        db.commit()
    else:
        print(f"No address found with the provided data for {Person.getAddress()}, {Person.getStreet()}, {Person.getSnumber()}.")
    db.close()
    
def seedUser(User):
    updata=[User.getEmail(),User.getPhone(),User.getIBAN()]
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute(
        "SELECT id FROM Person WHERE email = ? AND phone = ? AND iban = ?"
        , (updata))
    PersonID=cur.fetchone()
    if PersonID:
        PersonID=PersonID[0]
        data=[User.getUsername(),User.getPassword(),0,PersonID]
        cur.execute("""INSERT INTO User (
            username,
            password,
            adminrole,
            PersonID
            ) VALUES (?, ?, ?, ?);""", data)
        db.commit()
    else:
        print(f"No address found with the provided data for {User.getEmail()}, {User.getPhone()}, {User.getIBAN()}.")
    db.close()
    
def seedUserComplete(User,Person,Address):
    seedAddress(Address)
    seedPerson(Person)
    seedUser(User)
    
def seedCustomer(Customer):
    cpdata=[Customer.getEmail(),Customer.getPhone(),Customer.getIBAN()]
    db=sqlite3.connect('user.db')    
    cur=db.cursor()
    cur.execute(
        "SELECT id FROM Person WHERE email = ? AND phone = ? AND iban = ?"
        , (cpdata))
    PersonID=cur.fetchone()
    if PersonID:
        PersonID=PersonID[0]
        data=[Customer.getCompany(),PersonID]
        cur.execute("""INSERT INTO Customer (
            company,
            PersonID
            ) VALUES (?, ?);""", data)
        db.commit()
    else:
        print(f"No address found with the provided data for {Customer.getEmail()}, {Customer.getPhone()}, {Customer.getIBAN()}.")
    db.close()

def seedCustomerComplete(Customer,Person,Address):
    seedAddress(Address)
    seedPerson(Person)
    seedCustomer(Customer)
# --- search ---
def searchUserDB(search):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute(
        """SELECT User.*, Person.*, Address.* 
        FROM User 
        JOIN Person ON User.PersonID = Person.ID
        JOIN Address ON Person.AddressID = Address.ID
        WHERE User.ID LIKE ? OR 
        User.username LIKE ? OR 
        User.PersonID LIKE ? OR
        Person.name LIKE ? OR
        Person.firstname LIKE ? OR
        Person.email LIKE ? OR
        Person.phone LIKE ? OR
        Person.iban LIKE ? OR
        Address.country LIKE ? OR
        Address.zip LIKE ? OR
        Address.city LIKE ? OR
        Address.street LIKE ? OR
        Address.snumber LIKE ?;
        """, (search,)*13)
    results=cur.fetchall()
    db.close()
    return results
    
def searchCustomerDB(search):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute(
        """SELECT Customer.*, Person.*, Address.* 
        FROM Customer 
        JOIN Person ON Customer.PersonID = Person.ID
        JOIN Address ON Person.AddressID = Address.ID
        WHERE Customer.ID LIKE ? OR 
        Customer.company LIKE ? OR 
        Customer.PersonID LIKE ? OR
        Person.name LIKE ? OR
        Person.firstname LIKE ? OR
        Person.email LIKE ? OR
        Person.phone LIKE ? OR
        Person.iban LIKE ? OR
        Address.country LIKE ? OR
        Address.zip LIKE ? OR
        Address.city LIKE ? OR
        Address.street LIKE ? OR
        Address.snumber LIKE ?;
        """, (search,)*13)
    results=cur.fetchall()
    db.close()
    return results

# --- delete ---    
def deleteCustomerN(name,firstname,email,phone,iban):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    try:
        cur.execute("SELECT ID FROM Person WHERE name = ? AND firstname = ? AND email = ? AND phone = ? AND iban = ?", (name,firstname,email,phone,iban))
        PersonID=cur.fetchone()
        if PersonID:
            PersonID=PersonID[0]
            cur.execute("SELECT AddressID FROM Person WHERE ID = ?", (PersonID,))
            AddressID=cur.fetchone()        
            if AddressID:
                AddressID=AddressID[0]
                cur.execute("SELECT ID FROM Customer WHERE PersonID = ?", (PersonID,))
                CustomerID=cur.fetchone()        
                if CustomerID:
                    CustomerID=CustomerID[0]
                    cur.execute("DELETE FROM Customer WHERE ID = ?", (CustomerID,))
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Customer WHERE PersonID = ?",(PersonID,))
                    pidcount=cur.fetchone()[0]
                    if pidcount==0:
                        cur.execute("DELETE FROM Person WHERE ID = ?",(PersonID,))
                        print(f"{PersonID} deleted from Person.")
                    else:
                        print("Cannot delete from Person because it is referenced in Customer.")
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Person WHERE AddressID = ?",(AddressID,))
                    aidcount=cur.fetchone()[0]
                    if aidcount==0:
                        cur.execute("DELETE FROM Address WHERE ID = ?",(AddressID,))
                        print(f"{AddressID} deleted from Address.")
                    else:
                        print("Cannot delete from Address because it is referenced in Person.")
                    db.commit()
                    db.close()
                else:
                    print(f"No address found with the provided data for {CustomerID}.")
            else:
                print(f"No address found with the provided data for {AddressID}.")
        else:
            print(f"No address found with the provided data for {PersonID}.")
    except sqlite3.Error as e:
        print(f"an error occurred: {e}")
    db.close()
    
def deleteCustomerID(CustomerID):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    try:
        cur.execute("SELECT PersonID FROM Customer WHERE ID = ?", (CustomerID,))
        PersonID=cur.fetchone()
        if PersonID:
            PersonID=PersonID[0]
            cur.execute("SELECT AddressID FROM Person WHERE ID = ?", (PersonID,))
            AddressID=cur.fetchone()        
            if AddressID:
                AddressID=AddressID[0]
                if CustomerID:
                    cur.execute("DELETE FROM Customer WHERE ID = ?", (CustomerID,))
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Customer WHERE PersonID = ?",(PersonID,))
                    pidcount=cur.fetchone()[0]
                    if pidcount==0:
                        cur.execute("DELETE FROM Person WHERE ID = ?",(PersonID,))
                        print(f"{PersonID} deleted from Person.")
                    else:
                        print("Cannot delete from Person because it is referenced in Customer.")
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Person WHERE AddressID = ?",(AddressID,))
                    aidcount=cur.fetchone()[0]
                    if aidcount==0:
                        cur.execute("DELETE FROM Address WHERE ID = ?",(AddressID,))
                        print(f"{AddressID} deleted from Address.")
                    else:
                        print("Cannot delete from Address because it is referenced in Person.")
                    db.commit()
                    db.close()
                else:
                    print(f"No address found with the provided data for {CustomerID}.")
            else:
                print(f"No address found with the provided data for {AddressID}.")
        else:
            print(f"No address found with the provided data for {PersonID}.")
    except sqlite3.Error as e:
        print(f"an error occurred: {e}")
    db.close()

def deleteUserN(username):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    try:
        cur.execute("SELECT ID FROM User WHERE username = ?", (username,))
        UserID=cur.fetchone()
        if UserID:
            UserID=UserID[0]
            cur.execute("SELECT PersonID FROM User WHERE ID = ?", (UserID,))
            PersonID=cur.fetchone()        
            if PersonID:
                PersonID=PersonID[0]
                cur.execute("SELECT AddressID FROM Person WHERE ID = ?", (PersonID,))
                AddressID=cur.fetchone()
                if AddressID:
                    AddressID=AddressID[0]
                    cur.execute("DELETE FROM User WHERE ID = ?", (UserID,))
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Customer WHERE PersonID = ?",(PersonID,))
                    pidcount=cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM User WHERE PersonID = ?",(PersonID,))
                    uidcount=cur.fetchone()[0]
                    if pidcount==0 and uidcount==0:
                        cur.execute("DELETE FROM Person WHERE ID = ?",(PersonID,))
                        print(f"{PersonID} deleted from Person.")
                    else:
                        print("Cannot delete from Person because it is referenced in other table.")
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Person WHERE AddressID = ?",(AddressID,))
                    aidcount=cur.fetchone()[0]
                    if aidcount==0:
                        cur.execute("DELETE FROM Address WHERE ID = ?",(AddressID,))
                        print(f"{AddressID} deleted from Address.")
                    else:
                        print("Cannot delete from Address because it is referenced in Person.")
                    db.commit()
                    db.close()
                else:
                    print(f"No address found with the provided data for {AddressID}.")
            else:
                print(f"No address found with the provided data for {PersonID}.")
        else:
            print(f"No address found with the provided data for {UserID}.")
    except sqlite3.Error as e:
        print(f"an error occurred: {e}")
    db.close()

def deleteUserID(UserID):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    try:
        if UserID:
            cur.execute("SELECT PersonID FROM User WHERE ID = ?", (UserID,))
            PersonID=cur.fetchone()        
            if PersonID:
                PersonID=PersonID[0]
                cur.execute("SELECT AddressID FROM Person WHERE ID = ?", (PersonID,))
                AddressID=cur.fetchone()
                if AddressID:
                    AddressID=AddressID[0]
                    cur.execute("DELETE FROM User WHERE ID = ?", (UserID,))
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Customer WHERE PersonID = ?",(PersonID,))
                    pidcount=cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM User WHERE PersonID = ?",(PersonID,))
                    uidcount=cur.fetchone()[0]
                    if pidcount==0 and uidcount==0:
                        cur.execute("DELETE FROM Person WHERE ID = ?",(PersonID,))
                        print(f"{PersonID} deleted from Person.")
                    else:
                        print("Cannot delete from Person because it is referenced in other table.")
                    db.commit()
                    cur.execute("SELECT COUNT(*) FROM Person WHERE AddressID = ?",(AddressID,))
                    aidcount=cur.fetchone()[0]
                    if aidcount==0:
                        cur.execute("DELETE FROM Address WHERE ID = ?",(AddressID,))
                        print(f"{AddressID} deleted from Address.")
                    else:
                        print("Cannot delete from Address because it is referenced in Person.")
                    db.commit()
                    db.close()
                else:
                    print(f"No address found with the provided data for {AddressID}.")
            else:
                print(f"No address found with the provided data for {PersonID}.")
        else:
            print(f"No address found with the provided data for {UserID}.")
    except sqlite3.Error as e:
        print(f"an error occurred: {e}")
    db.close()
    
def updateUser():
    db=sqlite3.connect('user.db')
    
    db.commit()
    db.close()
    
def updateCustomer():
    db=sqlite3.connect('user.db')
    
    db.commit()
    db.close()
# --- login ---
def readLoginDB(username, password):
    db=sqlite3.connect('user.db')
    cur=db.cursor()
    
    cur.execute("SELECT PersonID FROM User WHERE username = ? AND password = ?", (username, password))
    PersonID=cur.fetchone()
    
    if PersonID:
        PersonID=PersonID[0]
        cur.execute("SELECT AddressID FROM Person WHERE ID = ?", (PersonID,))
        AddressID=cur.fetchone()        
        adata=None
        if AddressID:
            AddressID=AddressID[0]
            cur.execute("SELECT country, zip, city, street, snumber FROM Address WHERE ID = ?", (AddressID,))
            adata=cur.fetchone()
        cur.execute("SELECT name, firstname, email, phone, iban FROM Person WHERE ID = ?", (PersonID,))
        pdata=cur.fetchone()
        cur.execute("SELECT username, password FROM User WHERE username = ? AND password = ?", (username, password))
        udata=cur.fetchone()
        cur.execute("SELECT adminrole FROM User WHERE username = ? AND password = ?", (username, password))
        admincheck=cur.fetchone()
        
        db.commit()
        db.close()
        
        return {
            'Address': adata,
            'Person': pdata,
            'User': udata,
            'Admin': admincheck[0] if admincheck else None
        }
    else:
        print(f"No user found with the provided data for {username}.")
        db.commit()
        db.close()
        return 