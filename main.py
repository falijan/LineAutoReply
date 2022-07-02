
from fastapi import FastAPI, Request, Header, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent, LeaveEvent

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session
from SourceTable import Source

line_bot_api = LineBotApi('3EyCQCCLyB02oXfxM5rD9fXjCZ0NWkqe/PPoCafOt1fYWdSC8PYPr87t0j/BpGSsWCqCTjiRrffXGv8B1W+3yqv/AI87caSFPcrCX8NXKLjvkZEVcgzK6AKlU6b2C144lr7jTXYRMpO+vfcqvebnnQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7ddd099b6823a1cf03f8f4a35153c7f6')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_methods = ['*'],
    allow_headers = ['*'],
    allow_credentials = True
)


engine = create_engine("sqlite+pysqlite:///sqlsample.db3", echo=True, future=True)

@app.post('/line')
async def line_root(request: Request, x_line_signature: str = Header(None)):
    try:
        body = await request.body()
        content = body.decode("utf-8")
        handler.handle(content, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
@handler.add(JoinEvent)
def join_group(event):
    try:
        with Session(engine) as session:
            if event.source.type == 'group':
                query = session.query(Source).filter(and_(Source.source_type == event.source.type, Source.group_id == event.source.group_id))

            if query.count() == 0:
                if event.source.type == 'group':
                    group = line_bot_api.get_group_summary(event.source.group_id)
                    new_source = Source(source_type = event.source.type, group_id = event.source.group_id, source_enabled = 1, group_name = group.group_name)

                session.add(new_source)
                session.commit()
            else:
                query.update({ "source_enabled": 1 })
                session.commit()
    except Exception as e:
        print('JoinEvent', e)

@handler.add(LeaveEvent)
def leave_group(event):
    try:
        with Session(engine) as session:
            if (event.source.type == 'group'):
                query = session.query(Source).filter(and_(Source.source_type == event.source.type, Source.group_id == event.source.group_id))

            query.update({ "source_enabled": 0 })
            session.commit()
    except Exception as e:
        print('LeaveEvent', e)
@app.post('/send')
async def send_message(request: Request):
    try:
        json = await request.json()
        with Session(engine) as session:
            if json['type'] == 'group':
                if json['id'] != '':
                    line_bot_api.push_message(json['id'], TextSendMessage(text=json['message']))
                else:
                    for g in session.query(Source).filter(and_(Source.group_name == json['name'], Source.source_enabled == 1)).all():
                        line_bot_api.push_message(g.group_id, TextSendMessage(text=json['message']))
    except Exception as e:
        print('Send', e)
        raise HTTPException(status_code=400, detail=e)