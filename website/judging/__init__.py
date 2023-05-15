from ..db import db
import subprocess, os, time, psutil, platform

class JudgeResult:
    def __init__(self, verdict, time, memory, message=None) -> None:
        self.verdict = verdict
        self.time = time
        self.memory = memory
        self.message = message
class RunCodeResult:
    def __init__(self, output, time, memory, error=None):
        self.output = output
        self.time = time
        self.memory = memory
        self.error = error

def compileCode(code) -> str | None:
    with open('./sandbox/submission.cpp', 'w', encoding="UTF8") as f:
        f.write(code)
    command = f'docker run --memory=100m --rm -v {os.getcwd()}/sandbox:/sandbox judge-sandbox /bin/sh -c "cd /sandbox && g++ submission.cpp -o submission 2>&1 >/dev/null"'
    execute = subprocess.Popen(command, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = execute.communicate(timeout=3000)
    if execute.returncode == 1: return result[0]

def runCode(inputData, timeLimit, memoryLimit) -> RunCodeResult:
    with open('./sandbox/data.in', 'w', encoding="UTF8") as f:
        f.write(inputData)
    command = f'docker run --memory={memoryLimit}m --rm -v {os.getcwd()}/sandbox:/sandbox judge-sandbox /bin/sh -c "cd /sandbox && ./submission < data.in"'
    startTime = time.time()
    try:
        execute = subprocess.Popen(command, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        memoryUsage = int(psutil.Process(execute.pid).memory_info().rss / 1024 / 1024)
        result = execute.communicate(timeout=timeLimit / 1000 + 2)
        timeUsage = round(max(time.time() - startTime - 1, 0) * 1000)
        if (execute.returncode != 0):
            return RunCodeResult(result[0], timeUsage, memoryUsage, "Compile Error")
        else:
            return RunCodeResult(result[0], timeUsage, memoryUsage)
    except subprocess.TimeoutExpired:
        return RunCodeResult("TLE", timeLimit, int(psutil.Process(execute.pid).memory_info().rss / 1024 / 1024), "TLE")
    
def judgeCode(inputData, answerData:str, timeLimit, memoryLimit) -> JudgeResult:
    runCodeResult = runCode(inputData, timeLimit, memoryLimit)
    if runCodeResult.error != None:
        return JudgeResult(runCodeResult.output, runCodeResult.time, runCodeResult.memory, runCodeResult.error)
    elif runCodeResult.output.strip() == answerData.strip():
        return JudgeResult("AC", runCodeResult.time, runCodeResult.memory)
    else:
        return JudgeResult("WA", runCodeResult.time, runCodeResult.memory)

def judgement(problemID, code, submissionID):
    problemData = db['problems'].find_one({'pid': problemID})
    submissionDataDocument = db['submission_data']
    submissionData = submissionDataDocument.find_one({'_id': submissionID})
    timeLimit = problemData['time_limit']
    memoryLimit = problemData['memory_limit']
    print(f"Compiling {problemID}")
    compileResult = compileCode(code)
    print(f"Compile Finish")
    if compileResult != None:
        submissionData.update({'done': 1, 'verdict': 'Compile Error', 'error_msg': compileResult})
        submissionDataDocument.replace_one({'_id': submissionID}, submissionData)
        return
    previousTestcase = 1
    currentTestcase = 0
    subtaskJudgeResults = {
        "RE": 0,
        "TLE": 0,
        "MLE": 0,
        "WA": 0,
        "AC": 0,
    }
    maxTimeUsage = 0
    maxMemoryUsage = 0
    for subtaskRange in problemData['subtask_range']:
        subtaskRange = int(subtaskRange)
        for subtask in range(previousTestcase, subtaskRange + 1):
            print(f"Judging {problemID} {subtask}")
            testcaseFilePath = f"./test_data/{problemID}/{subtask}"
            inputData = "";
            answerData = "";
            with open(testcaseFilePath + ".in", 'r') as f:
                inputData = f.read()
            with open(testcaseFilePath + ".out", 'r') as f:
                answerData = f.read()
            judgeResult = judgeCode(inputData, answerData, timeLimit, memoryLimit)
            submissionData['subtask'][currentTestcase][subtask - previousTestcase] = [
                judgeResult.verdict,
                judgeResult.time,
                judgeResult.memory
            ]
            print("Judge Result", judgeResult.verdict, judgeResult.time, judgeResult.memory)
            maxTimeUsage = max(maxTimeUsage, judgeResult.time)
            maxMemoryUsage = max(maxMemoryUsage, judgeResult.memory)
            subtaskJudgeResults[judgeResult.verdict] += 1
            submissionData['error_msg'] = judgeResult.message
            submissionDataDocument.replace_one({'_id': submissionID}, submissionData)
        previousTestcase = subtaskRange + 1
        currentTestcase += 1
    finalVerdict = "validation Error"
    for verdict in subtaskJudgeResults:
        if subtaskJudgeResults[verdict] > 0:
            finalVerdict = verdict
            break
        
    submissionDataDocument.update_one({
        '_id': submissionID
    }, {
        '$set': {
            'done': 1,
            'verdict': finalVerdict,
            'exetime': maxTimeUsage
        }
    })
    currentSubmissionUserID = submissionData['userid']
    if finalVerdict == "AC":
        SolvedProblems = db['account'].find_one({'name': currentSubmissionUserID})['solved']
        ACCount = db['account'].find_one({'name': currentSubmissionUserID})['AC']
        if problemID not in SolvedProblems:
            SolvedProblems.append(problemID)
            db['account'].update_one({'name': currentSubmissionUserID}, {'$set': {'solved': SolvedProblems, 'AC':ACCount+1}})
            
    submissionData.update({'done': 1, 'verdict': finalVerdict, 'exetime': maxTimeUsage})
    submissionDataDocument.replace_one({'_id': submissionID}, submissionData)