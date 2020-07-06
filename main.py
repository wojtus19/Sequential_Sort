import random as rand
from math import pow
import sys
import re
import tkinter as tk
import os


maxDigit = 6 # maksymalna długość składowej wektora
dimensions = 2 #liczba wymiarów wektorów
vectorsInBuffer = 256
bufferLength = vectorsInBuffer*(maxDigit*dimensions + (dimensions)) #długość buffora = 128 wektorów +dimensions, bo przecinki i \n na koncu
writings = 0
readings = 0

def generateRandomSeries():
    NumOfRecords = input("Wybierz liczbę rekordów do wygenerowania: \n")
    output = sys.stdout
    file_ = open("records.txt", "a")
    sys.stdout = file_
    for _ in range(int(NumOfRecords)):
        for i in range(dimensions):
            tmp = rand.randint(0, pow(10, maxDigit)-1 )
            if(i != dimensions - 1):
                print(str(tmp).zfill(maxDigit), end=',')
            else:
                print(str(tmp).zfill(maxDigit))
    sys.stdout = output
    file_.close()

def getVectorFromRecordLine(record):
    vec = re.findall('\\d+',record)
    return vec


def inputRecord(fileName):
    record = ""
    for i in range(dimensions):
        tmp = input("Wprowadź " + str(i+1) + ". współrzędną (Niewiększą niż " + str(int(pow(10,maxDigit)-1)) +")  ")
        while (int(tmp) > pow(10, maxDigit)-1 ):
            print("Podana wielkość jest zbyt duża")
            tmp = input("Wprowadź " + str(i+1) + ". współrzędną (Niewiększą niż " + str(int(pow(10,maxDigit)-1)) +")  ")
        if(i != dimensions - 1):
            record += (str(tmp).zfill(maxDigit) + ',')
        else:
           record += (str(tmp).zfill(maxDigit))
    record += "\n"
    Write(record, fileName)

def printRecords(fileName, phase):
    root = tk.Tk()
    S = tk.Scrollbar(root)
    T = tk.Text(root, height=50, width=dimensions*10 + 30)
    S.pack(side=tk.RIGHT, fill=tk.Y)
    T.pack(side=tk.LEFT, fill=tk.Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set) 
    f = open(fileName, 'r')
    T.insert(tk.END, "Rekordy z pliku: " + str(fileName)+"\n")
    if(phase != ""):
        T.insert(tk.END, "Faza: " + str(phase)+"\n")
    while(True):
        record = f.readline()
        if(record != ''):
            getVectorFromRecordLine(record)
            vecLen = str("%.2f" % round(calculateLength(record),2))
            T.insert(tk.END, str(getVectorFromRecordLine(record)) + " => Długość: " + vecLen + "\n")
        else:
            break
    root.mainloop()
    f.close()

def Distribution(fileName):
    global readings
    global writings
    TruncateFile("t1.txt")
    TruncateFile("t2.txt")
    actualTape = "t1"
    isSorted = True
    startingByte = 0
    buffer = Read(fileName, startingByte, bufferLength)
    startingByte += len(buffer)+vectorsInBuffer
    buffer = buffer.splitlines()
    readings += 1
    buffLength = len(buffer)
    prev = buffer[0]
    bufferToWrite1 = ""
    bufferToWrite2 = ""
    bufferToWrite1 += str(prev + "\n")
    vecInBufferToWrite1 = 1             # funckja write() tak naprawdę nie wpisuje od razu danej do pliku, dopiero po wywołaniu funkcjiclose() lub przepełnieniu buforu 
    vecInBufferToWrite2 = 0             # systemowego, dlatego wywoluje funkcje flush() i os.fsync() aby wiedziec kiedy nastepuje zapis
    i = 1
    while(buffer != []):
        actual = buffer[i]
        if(isGreater(prev, actual) and actualTape == "t1"):
            actualTape = "t2"
            isSorted = False
        elif(isGreater(prev,actual) and actualTape == "t2"):
            actualTape = "t1"
        if(actualTape == "t1"):
            bufferToWrite1 += str(actual + "\n")
            vecInBufferToWrite1 += 1
        elif(actualTape == "t2"):
            bufferToWrite2 += str(actual + "\n")
            vecInBufferToWrite2 += 1
        prev = actual
        if(i == vectorsInBuffer - 1):
            buffer = Read(fileName, startingByte, bufferLength)
            startingByte += len(buffer)+vectorsInBuffer
            buffer = buffer.splitlines()
            i = 0
            buffLength = len(buffer)
        elif(i == buffLength - 1):
            break
        else:
            i += 1
        if (vecInBufferToWrite1 >= vectorsInBuffer): # zapisz na dysk jeżeli vectorów w buforze jest wiecej niż ustalone
            Write(bufferToWrite1, "t1.txt")
            vecInBufferToWrite1 = 0
            bufferToWrite1 = ""
        if (vecInBufferToWrite2 >= vectorsInBuffer): # zapisz na dysk jeżeli vectorów w buforze jest wiecej niż ustalone
            Write(bufferToWrite2, "t2.txt")
            vecInBufferToWrite2 = 0
            bufferToWrite2 = ""
    Write(bufferToWrite1, "t1.txt")
    Write(bufferToWrite2, "t2.txt")
    return isSorted

def Write(buffer, fileName):
    global writings
    f = open(fileName, 'a')
    f.write(buffer)
    writings += 1
    f.close()

def TruncateFile(fileName):
    global writings
    f = open(fileName, "w")
    f.truncate()
    writings += 1
    f.close()

def Read(fileName, startingByte, length):
    global readings
    f = open(fileName, 'r')
    readings += 1
    f.seek(startingByte)
    buffer = f.read(length)
    f.close()
    return buffer

def Merge():
    vecInBufferToWrite = 0
    startingByte1 = 0
    startingByte2 = 0
    TruncateFile("t3.txt")                        # Wyczyść plik
    buffer1 = Read("t1.txt", startingByte1, bufferLength)
    buffer2 = Read("t2.txt", startingByte2, bufferLength)
    startingByte1 += len(buffer1)+vectorsInBuffer
    startingByte2 += len(buffer2)+vectorsInBuffer
    buffer1 = buffer1.splitlines()
    buffer2 = buffer2.splitlines()
    bufferToWrite = ""
    counter1 = 0
    counter2 = 0
    series1 = True
    series2 = True
    t1Ended = False
    t2Ended = False
    while (len(buffer1) != 0 or len(buffer2) != 0):
        if (series1 == False and series2 == False):                     # Jeżeli skonczyly sie serie w T1 i T2 to zacznij od nowa
            if(not t1Ended):
                series1 = True
            if(not t2Ended):
                series2 = True
        if (series1 == True and series2 == True):                       # Jeżeli w środku obu serii to porównaj taśmy
            if (isGreater(buffer1[counter1],buffer2[counter2])):
                tape = "t2"
                prev = buffer2[counter2]
                counter2 += 1
                if (counter2 < len(buffer2)):
                    if(isGreater(buffer2[counter2-1],buffer2[counter2])):
                        tape = "t1"
                        series2 = False
            else:
                tape = "t1"
                prev = buffer1[counter1]
                counter1 += 1
                if (counter1 < len(buffer1)):
                    if(isGreater(buffer1[counter1-1],buffer1[counter1])):
                        tape = "t2"
                        series1 = False
        elif (series1 == False and series2 == True):                    # Jeżeli T1 się skończyła to przepisz z T2
                tape = "t2"
                prev = buffer2[counter2]
                counter2 += 1
                if (counter2 < len(buffer2)):
                    if(isGreater(buffer2[counter2-1],buffer2[counter2])):
                        series2 = False
        elif (series1 == True and series2 == False):                    # Jeżeli T2 się skończyła  to przepisz z T1
                tape = "t1"
                prev = buffer1[counter1]
                counter1 += 1
                if (counter1 < len(buffer1)):
                    if(isGreater(buffer1[counter1-1],buffer1[counter1])):
                        series1 = False
                        
        bufferToWrite += str(prev) + "\n"                               # Wpisz rekord do bufora
        vecInBufferToWrite += 1     
        if(vecInBufferToWrite >= vectorsInBuffer):                      # jeśli w buforze jest wystarczająco dużo rekordów
            Write(bufferToWrite, "t3.txt")              # Wpisz bufor do pliku, potem wyczyść bufor
            vecInBufferToWrite = 0
            bufferToWrite = ""

        if(counter1 == len(buffer1)):
            buffer1 = Read("t1.txt",startingByte1, bufferLength)
            startingByte1 += len(buffer1)+vectorsInBuffer
            buffer1 = buffer1.splitlines()
            if(buffer1 != []):
                counter1 = 0
                if(tape == "t1" and isGreater(prev,buffer1[counter1])):     #sprawdzenie konca serii dla T1, jeżeli tak to przepisujemy z T2
                    series1 = False
                    tape = "t2"
            else:
                t1Ended = True
                series1 = False
        if(counter2 == len(buffer2)):
            buffer2 = Read("t2.txt", startingByte2, bufferLength)
            startingByte2 += len(buffer2)+vectorsInBuffer
            buffer2 = buffer2.splitlines()
            if(buffer2 != []):
                counter2 = 0
                if(tape ==  "t2" and isGreater(prev, buffer2[counter2])):   #sprawdzenie konca serii dla T2, jezeli tak to przepisujemy z T1
                    series2 = False
                    tape = "t1"
            else:
                t2Ended = True
                series2 = False
    Write(bufferToWrite, "t3.txt")

def calculateLength(vec):
    vec_ = getVectorFromRecordLine(vec)
    sum = 0
    for i in vec_:
        sum+= pow(int(i), dimensions)
    sum = sum**(1./dimensions)
    return sum

def isGreater(a,b):
    if (calculateLength(a) > calculateLength(b)):
        return True
    else:
        return False


def main():
    fileName = "records.txt"
    while(1):
        print("1. Wygeneruj N losowych rekordów \n2. Wstaw rekord ręcznie \n3. Importuj rekordy z pliku \n4. Wypisz plik z rekordami \n5. Sortuj \n6. Sortuj z odczytem taśmy po każdej fazie \n7. Wypisz dowolny plik z rekordami \n8. Wyjdź")
        option = input()
        if (option == "1"):
            generateRandomSeries()
        elif(option == "2"):
            inputRecord(fileName)
        elif(option == "3"):
            fileName = input("Wpisz ścieżkę do pliku:  ")
        elif(option == "4"):
            printRecords(fileName, "")
        elif(option == "5" or option == "6"):
            firstDistribution = True
            phase = 0
            while(Distribution(fileName) == False):
                Merge()
                phase += 1
                if(option == "6"):
                    printRecords(fileName, str(phase))
                if(firstDistribution):
                    firstDistribution = False
                    fileName = "t3.txt"
            printRecords("t3.txt", "Zakończono sortowanie")
            print("\n==========\nZakończono sortowanie")
            print("Liczba odczytów: " + str(readings))
            print("Liczba zapisów: " + str(writings))
            print("Liczba Faz: " + str(phase) + "\n==========\n")
            fileName = "records.txt"
        elif(option == "7"):
            fN = input("Wprowadź nazwę pliku do wypisania rekordu: ")
            printRecords(fN, "")
        elif(option == "8"):
            break
        else:
            print("Wprowadź poprawną cyfrę")

if __name__ == "__main__":
    main()