# This program allows you to look up any paragraph of various German tax codes

# Crawler
import requests, bs4, os, re
import io
import webbrowser
import time
import keyboard

# GUI
#from tkinter import HtmlFrame
import tkinter as tk 
from tkinter import ttk
import threading

def get_law(law,section,paragraph):
    url = "https://dejure.org/gesetze/" + law
    
    if section != "":
        url += "/" + section + ".html"

    res = requests.get(url)
    res.raise_for_status()
    time.sleep(1)

    ArticleSoup = bs4.BeautifulSoup(res.text, features="lxml")

    if section == "":
        head = ArticleSoup.find("div", id="headgesetz")
        text_box.insert(tk.END,head.getText())

        body = ArticleSoup.find("div", class_="gesetzestext")
        text_box.insert(tk.END,body.getText())

    else:
        title = ArticleSoup.find("h1")
        text_box.insert(tk.END,title.getText("\n")+ "\n\n")

        gesetzestext = ArticleSoup.find(id="gesetzestext")

        # If paragraph is not specified, give entire section
        if paragraph == "":
            text_box.insert(tk.END,gesetzestext.getText())
        else:
            text_box.insert(tk.END, gesetzestext.find_all("p")[int(paragraph)-1].getText() +"\n")

# Übersicht über Urteile
def get_verdicts(law,section):
    print("Getting verdicts...")
    def filter_verdicts(pattern):
        filter_count = 0
        verdict_widget.delete(0,tk.END)
        for key,value in tips.items():
            if re.search(pattern,key):
                verdict_widget.insert(tk.END,key)
                filter_count += 1
            if re.search(pattern,value):
                verdict_widget.insert(tk.END,key)
                filter_count += 1
        tooltip.set("Ich habe " + str(filter_count) + " Urteile gefunden.")
    
    def goto_verdict(verdictlink):
        url_verdict = "https://dejure.org/" + verdictlink

        res_verdict = requests.get(url_verdict)
        res_verdict.raise_for_status()
        time.sleep(1)

        VerdictSoup = bs4.BeautifulSoup(res_verdict.text, features="lxml")

        goto = VerdictSoup.find("a", class_="link_extern")
        print(goto)
        goto_link = "https://dejure.org/" + goto.get("href")

        webbrowser.open(goto_link)

        res_verdict_text = requests.get(goto_link)

        chunksize = 10000
        os.makedirs("./Verdicts", exist_ok=True)
        filename = verdict_widget.get(verdict_widget.curselection()).replace(".","-").replace(",","-").replace(" ","").replace("/","-")

        with io.open(os.path.join("Verdicts", filename + ".html"), "w+", encoding = "UTF8") as f:
            #for chunk in res_verdict_text.iter_content(chunk_size=chunksize):
                f.write(res_verdict_text.text)

    def reset_verdicts():
        verdict_widget.delete(0,tk.END)

        for l in verdicts.keys():
            verdict_widget.insert(tk.END,l)

        tooltip.set("Ich habe " + str(len(verdicts)) + " Urteile gefunden.")


    text_box.insert("1.0", "Getting verdicts from page 1...\n")
    url = "https://dejure.org/dienste/lex/" + law + "/" + section + "/1.html"

    res = requests.get(url)
    res.raise_for_status()
    time.sleep(1)

    ArticleSoup = bs4.BeautifulSoup(res.text, features="lxml")

    links = ArticleSoup.select('li[style="margin-bottom:8px;"]')

    if links:
        text_box.insert("2.0", "Success.\n")

    verdicts = dict()
    tips = dict()
    for l in links:
        verdicts[l.a.getText()] = l.a.get("href")
        tips[l.a.getText()] = l.getText()

    # Verdict window
    try:
        i = 2
        keep_going = True
        while keep_going:
            print("Getting verdicts from page",i)

            if keyboard.is_pressed("esc"):
                keep_going = False
                print("Operation terminated by user.")
                text_box.insert("1.0", "Operation terminated by user.\n")
                

            text_box.insert("1.0", "Getting verdicts from page " + str(i) + "...\n")
            text_box.insert("1.0", "Press Escape to stop.\n")
            url = "https://dejure.org/dienste/lex/" + law + "/" + section + "/" + str(i) + ".html"

            res = requests.get(url)
            res.raise_for_status()
            time.sleep(1)

            ArticleSoup = bs4.BeautifulSoup(res.text, features="lxml")

            links = ArticleSoup.select('li[style="margin-bottom:8px;"]')

            if not links:
                text_box.insert("2.0", "Failure. No more pages.\n")
                keep_going = False
            else: 
                text_box.insert("2.0", "Success.\n")

            for l in links:
                verdicts[l.a.getText()] = l.a.get("href")
                tips[l.a.getText()] = l.getText()

            i += 1
    except Exception as e:
        print(e)


    result_window = tk.Toplevel(root)
    result_window.title("Verdicts")
    result_window.geometry("800x500")

    verdict_frame = tk.Frame(result_window)
    verdict_frame.place(relx=0.5, rely=0.05, relwidth = 0.9, relheight=0.4, anchor = "n")

    verdict_widget = tk.Listbox(verdict_frame)
    verdict_widget.place(relwidth=0.975,relheight=1)
    scrollb2 = tk.Scrollbar(verdict_frame, command = verdict_widget.yview)
    scrollb2.place(relx = 0.975,relwidth = 0.025,relheight=1)
    verdict_widget['yscrollcommand'] = scrollb2.set

    for l in verdicts.keys():
        verdict_widget.insert(tk.END,l)

    desc_frame = tk.Frame(result_window)
    desc_frame.place(relx=0.5, rely=0.45, relwidth = 0.9, relheight=0.3, anchor = "n")

    tooltip = tk.StringVar(value = "Ich habe " + str(len(verdicts)) + " Urteile gefunden.")
    l1 = tk.Label(desc_frame, textvariable=tooltip)
    l1.place(relwidth=1,relheight=1)

    interact_frame = tk.Frame(result_window)
    interact_frame.place(relx=0.5, rely=0.75, relwidth = 0.9, relheight=0.2, anchor = "n")

    b1 = tk.Button(interact_frame,text = "Worum geht's?", command = lambda: tooltip.set( \
        tips[verdict_widget.get(verdict_widget.curselection())]))
    b1.place(rely=0.5, relwidth=0.5,relheight=0.5)

    b2 = tk.Button(interact_frame,text = "Zum Urteil!", command=lambda: goto_verdict(verdicts[verdict_widget.get(verdict_widget.curselection())]))
        #webbrowser.open("https://dejure.org/" + verdicts[verdict_widget.get(verdict_widget.curselection())]))
    b2.place(relx=0.5, rely=0.5,relwidth=0.5,relheight=0.5)

    l3 = tk.Button(interact_frame, text= "Zu viel! Filter nach", command= lambda: filter_verdicts(b3.get()))
    l3.place(relx=0, relwidth=0.333,relheight=0.5)
    
    b3 = tk.Entry(interact_frame,text= "Year")
    b3.place(relx=0.333, relwidth=0.333,relheight=0.5)

    b4 = tk.Button(interact_frame, text="Reset", command = lambda: reset_verdicts())
    b4.place(relx=0.666, relwidth=0.333,relheight=0.5)

def thread_verdicts(law,section):
    t = threading.Thread(target=get_verdicts,args=[law,section])
    t.start()


# Awesome GUI
if __name__== "__main__":

    root = tk.Tk()
    root.title("I AM THE LAW")
    root.geometry("700x500")

    print_frame = tk.Frame(root)
    print_frame.place(relx = 0.5, rely=0.05, relwidth = 0.9, relheight=0.7, anchor="n")

    text_box = tk.Text(print_frame, wrap=tk.WORD)
    text_box.place(relwidth=0.975,relheight=1)
    scrollb = tk.Scrollbar(print_frame, command = text_box.yview)
    scrollb.place(relx = 0.975,relwidth = 0.025,relheight=1)
    text_box['yscrollcommand'] = scrollb.set

    control_frame = tk.Frame(root)
    control_frame.place(relx = 0.5, rely=0.8, relwidth = 0.9, relheight=0.15, anchor="n")

    WIDGETS_R1_NUM = 6
    WIDGETS_R2_NUM = 3
    ROWS = 2

    WWIDTH_R1 = 1 / WIDGETS_R1_NUM
    WWIDTH_R2 = 1 / WIDGETS_R2_NUM

    RHEIGHT = 1 / ROWS

    laws = ["AO", "BewG", "BGB", "ErbStG", "EStG", "HGB", ]

    WIDGETS_R1 = [tk.Label(control_frame, text = "Gesetz"), ttk.Combobox(control_frame, values = laws), \
        tk.Label(control_frame, text = "§"), tk.Entry(control_frame), \
            tk.Label(control_frame, text = "Abs."), tk.Entry(control_frame)]

    WIDGETS_R2 = [tk.Button(control_frame, text = "Hol mir den Gesetzestext!", command = lambda: get_law(WIDGETS_R1[1].get(), \
        WIDGETS_R1[3].get(),WIDGETS_R1[5].get())), tk.Button(control_frame, text = "Zeig mir Urteile!", \
            command=lambda:thread_verdicts(WIDGETS_R1[1].get(), WIDGETS_R1[3].get())), \
                tk.Button(control_frame, text = "Räum mal auf hier!", command=lambda: text_box.delete("1.0",tk.END))]

    for num, lab in enumerate(WIDGETS_R1):
        lab.place(relx = num*WWIDTH_R1, relwidth = WWIDTH_R1, relheight=RHEIGHT)

    for num, lab in enumerate(WIDGETS_R2):
        lab.place(relx = num*WWIDTH_R2, rely = RHEIGHT, relwidth = WWIDTH_R2, relheight=RHEIGHT)

    


    root.mainloop()
