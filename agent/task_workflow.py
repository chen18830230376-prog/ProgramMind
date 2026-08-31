"""
ProgramMind

LangGraph任务工作流

实现:
任务驱动智能Agent


支持:
1. 教师备课
2. 学习规划
3. 科研调研

"""


from typing import TypedDict, List


from .agent_tools import AgentTools



# =====================
# 状态定义
# =====================


class TaskState(TypedDict):


    task:str

    task_type:str

    steps:List[str]

    result:str





# =====================
# Agent工作流
# =====================


class ProgramMindWorkflow:



    def __init__(self):


        self.tools=AgentTools()



    # -----------------
    # 任务分析
    # -----------------

    def analyze_task(
        self,
        state
    ):


        task=state["task"]



        if "备课" in task:


            task_type="teacher"


            steps=[

                "分析课程目标",

                "检索知识资源",

                "生成教学方案"

            ]



        elif "论文" in task or "科研" in task:


            task_type="research"


            steps=[

                "分析研究主题",

                "整理相关文献",

                "生成研究综述"

            ]



        else:


            task_type="student"


            steps=[

                "分析学习目标",

                "检索知识",

                "生成学习建议"

            ]



        state["task_type"]=task_type

        state["steps"]=steps



        return state





    # -----------------
    # 执行任务
    # -----------------


    def execute_task(
        self,
        state
    ):


        task_type=state["task_type"]



        if task_type=="teacher":


            result=self.tools.execute(

                "rag",

                {

                "query":
                state["task"]

                }

            )



        elif task_type=="research":


            result=self.tools.execute(

                "paper",

                {

                "paper_text":
                state["task"]

                }

            )



        else:


            result=self.tools.execute(

                "learning",

                {

                "student_data":
                {
                "score":80
                }

                }

            )



        state["result"]=str(result)


        return state





    # -----------------
    # 工作流入口
    # -----------------


    def run(
        self,
        task
    ):


        state={

            "task":task,

            "task_type":"",

            "steps":[],

            "result":""

        }



        state=self.analyze_task(
            state
        )


        state=self.execute_task(
            state
        )



        return state





if __name__=="__main__":


    workflow=ProgramMindWorkflow()



    result=workflow.run(

        "帮我完成机器学习课程备课"

    )


    print(result)