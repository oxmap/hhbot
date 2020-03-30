# -*- coding: utf-8 -*-
import os
from telegram.ext import Updater, CommandHandler, Job
import requests

cacheNames = []
cacheEmplNames = []
cacheUrls = []

def parseAPI(bot, job):
    resp = requests.get('https://api.hh.ru/vacancies?specialization=1&area=90&currency=RUR&period=1&per_page=50')
    if resp.status_code != 200:
        bot.send_message(job.context, text="Something went wrong with headhunter API =(")
    else:
        jsonData = resp.json()['items']
        msgText = ""
        needShow = False
        # 
        f = open('output', 'w')
        for x in jsonData:
            name = x.get('name')
            emplName = x.get('employer')['name']
            url = x.get('alternate_url')
            if (not name in cacheNames) and (not emplName in cacheEmplNames) and (not url in cacheUrls):
                cacheNames.append(name)
                cacheEmplNames.append(emplName) 
                cacheUrls.append(url)
                msgText += name + '[[' + emplName + ']]' + '\n'+ url + '\n' + '\n'
                needShow = True
        if needShow:
            bot.send_message(job.context, text=msgText[:-2])
        f.close()

def start(bot, update, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    job = job_queue.run_repeating(parseAPI, 10, 1, context=chat_id)
    chat_data['job'] = job

    update.message.reply_text('Starting parsing headhunter...')


def stop(bot, update, chat_data):
    """Removes the job if the user changed their mind"""
    if 'job' not in chat_data:
        update.message.reply_text('Parsing is not starting!')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Updates stoped!')

def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("stop", stop, pass_chat_data=True))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()