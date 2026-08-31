"""
ProgramMind

项目统一启动入口


启动:

FastAPI

AI服务


"""


import uvicorn



from api.ai_api import app





def init_system():


    """
    系统初始化

    后续可以加入:

    1. 模型加载
    2. PGVector连接
    3. Redis连接
    4. 数据初始化

    """



    print("====================")

    print("ProgramMind AI启动")

    print("====================")



    print(

        "初始化大模型..."

    )


    print(

        "初始化知识库..."

    )


    print(

        "初始化Agent..."

    )



    print(

        "系统准备完成"

    )





if __name__=="__main__":



    init_system()



    uvicorn.run(

        app,


        host="0.0.0.0",


        port=8000

    )