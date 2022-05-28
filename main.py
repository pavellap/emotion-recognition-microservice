import wave
import os
import sys
import pickle
from array import array
import struct
import json

from utils import extract_feature

'''
Файл для проверки нейросетей в реальных условиях
'''

THRESHOLD = 300
RATE = 16000
FORMAT = 8


def silent(snd):
    """
    Проверяем что в сэпмле не одна тишина
    """
    if max(snd) < THRESHOLD:
        return True
    else:
        return False


def trim(snd):
    """
    Обрезаем куски тишины
    """

    def _trim(snd):
        snd_started = False
        r = array('h')

        for i in snd:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    snd = _trim(snd)

    snd.reverse()
    snd = _trim(snd)
    snd.reverse()
    return snd


def add_silence(snd, seconds):
    '''
    Добавляем немного тишины по краям
    '''
    r = array('h', [0 for i in range(int(seconds * RATE))])
    r.extend(snd)
    r.extend([0 for i in range(int(seconds * RATE))])
    return r


def recognize(filename):
    absPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    audiosDir = absPath + '/audios'
    filename1 = audiosDir + f"/{filename}"  # сюда записывать путь к тестируемой аудиозаписи в формате wav
    filename2 = audiosDir + '/processed.wav'  # сюда записываем путь к обработанной аудиозаписи в формате wav

    modelG = pickle.load(
        open(absPath + "/models/mlp_classifier_gender.model", "rb"))  # открываем модель гендерной нейросети
    # сюда записывать путь для сохранения отредактированной первой записи
    # лучше создать копию первой записи и переименовать в имя файла2

    r = array('h')  # создаем массив для сохранения данных аудиозаписи
    os.system(f"ffmpeg -y -i {filename1} -ac 1 -ar 16000 {filename2}")  # конвертируем с помощью FFmpeg в моно 16кГц
    wav = wave.open(filename2, "rb")
    sample_width = wav.getsampwidth()
    # sample_rate = wav.getframerate()
    data = struct.unpack("<" + str(wav.getnframes()) + "h", wav.readframes(wav.getnframes()))  # распаковываем

    r.extend(data)  # записываем данные аудио в массив
    if not silent(r):  # если не тишина
        r = trim(r)  # обрезаем

        # r = pitch(r, sample_rate)

        r = add_silence(r, 0.5)  # добавляем тишину
        r = struct.pack('<' + ('h' * len(r)), *r)  # запаковывем обратно для сохранения далее

        wf = wave.open(filename2, 'wb')  # сохраняем
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(r)
        wf.close()

        features = extract_feature(filename2, mfcc=True, chroma=True, mel=True,
                                   contrast=True, tonnetz=True).reshape(1, -1)  # извлекаем признаки

        resultG = modelG.predict(features)[0]  # предсказываем гендер

        if resultG == "male":  # если мальчик - то открываем мужскую модель и передаем запись в нее
            modelM = pickle.load(open(absPath + "/models/mlp_classifier_male.model", "rb"))
            resultM = modelM.predict(features)[0]
            return {
                "emotion": resultM,
                "gender": "male",
                "success": True
            }
        elif resultG == "female":  # иначе - в женскую
            modelF = pickle.load(open(absPath + "/models/mlp_classifier_male.model", "rb"))
            resultF = modelF.predict(features)[0]
            return {
                "emotion": resultF,
                "gender": "female",
                "success": True
            }
    else:
        return {
            "success": False,
            "reason": "silence"
        }


if __name__ == "__main__":
    # todo: добавить комменты к путям обработки
    print('sys: ', sys.argv)
    absPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    filename1 = sys.argv[1]  # сюда записывать путь к тестируемой аудиозаписи в формате wav
    filename2 = sys.argv[2]  # сюда записываем путь к обработанной аудиозаписи в формате wav
