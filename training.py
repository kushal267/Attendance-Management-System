import os
import sys
import warnings
import logging
import pickle
from pathlib import Path

import cv2
from deepface import DeepFace

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

warnings.filterwarnings('ignore', category=FutureWarning)
logging.getLogger('tensorflow').setLevel(logging.FATAL)
logging.getLogger('absl').setLevel(logging.FATAL)

def get_base_dir():
    from pathlib import Path   
    data_dir = Path.home() / "Documents" / "Face_Attendance_Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

"""def get_base_dir():
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
"""

"""def train_model(base_dir=None):
    base_dir = Path(base_dir) if base_dir is not None else get_base_dir()
    dataset_path = base_dir / "dataset"
    if not dataset_path.exists():
        raise FileNotFoundError("dataset folder not found. Register at least one student first.")

    print("Training Python :", sys.executable)
    known_embeddings = []
    known_ids = []
    known_names = []
    model_name = "Facenet"
    detector_backend = "opencv"

    print("Loading DeepFace model... this may take a moment.")

    persons = [d for d in os.listdir(dataset_path) if (dataset_path / d).is_dir()]
    if not persons:
        raise FileNotFoundError("No student folders found in dataset. Register at least one student.")

    for person in persons:
        person_path = dataset_path / person
        if not person_path.is_dir():
            continue

        if "_" in person and person.split("_", 1)[0].isdigit():
            user_id = int(person.split("_", 1)[0])
            user_name = person.split("_", 1)[1]
        else:
            user_id = -1
            user_name = person

        for image_name in os.listdir(person_path):
            image_path = person_path / image_name
            image = cv2.imread(str(image_path))

            if image is None:
                print(f"Skipping {image_path}: cannot read image")
                continue

            try:
                representations = DeepFace.represent(
                    img_path=image,
                    model_name=model_name,
                    detector_backend=detector_backend,
                    enforce_detection=False,
                    align=False,
                )
            except Exception as exc:
                print(f"Skipping {image_path}: represent failed ({exc})")
                continue

            if not representations:
                print(f"Skipping {image_path}: no face found")
                continue

            embedding = representations[0]["embedding"]
            known_embeddings.append(embedding)
            known_ids.append(user_id)
            known_names.append(user_name)

    if not known_embeddings:
        raise RuntimeError("No face embeddings found. Add images to dataset and try again.")

    with open(base_dir / "face_model.pkl", "wb") as f:
        pickle.dump((known_embeddings, known_ids, known_names), f)

    print("Training complete")
    print(f"Saved {len(known_embeddings)} face embeddings.")
    return base_dir / "face_model.pkl"
"""
def train_model(base_dir=None):
    base_dir = Path(base_dir) if base_dir is not None else get_base_dir()
    dataset_path = base_dir / "dataset"
    if not dataset_path.exists():
        raise FileNotFoundError("dataset folder not found. Register at least one student first.")

    known_embeddings = []
    known_ids = []
    known_names = []
    model_name = "Facenet"
    detector_backend = "opencv"
    
    deepface_error = "Unknown Error"

    persons = [d for d in os.listdir(dataset_path) if (dataset_path / d).is_dir()]
    if not persons:
        raise FileNotFoundError("No student folders found in dataset.")

    for person in persons:
        person_path = dataset_path / person
        if not person_path.is_dir():
            continue

        if "_" in person and person.split("_", 1)[0].isdigit():
            user_id = int(person.split("_", 1)[0])
            user_name = person.split("_", 1)[1]
        else:
            user_id = -1
            user_name = person

        for image_name in os.listdir(person_path):
            image_path = person_path / image_name
            image = cv2.imread(str(image_path))

            if image is None:
                continue

            try:
                representations = DeepFace.represent(
                    img_path=image,
                    model_name=model_name,
                    detector_backend=detector_backend,
                    enforce_detection=False,
                    align=False,
                )
            except Exception as exc:
              
                deepface_error = str(exc)
                continue

            if not representations:
                continue

            embedding = representations[0]["embedding"]
            known_embeddings.append(embedding)
            known_ids.append(user_id)
            known_names.append(user_name)

    if not known_embeddings:
        raise RuntimeError(f"AI Model Error:\n{deepface_error}")

    with open(base_dir / "face_model.pkl", "wb") as f:
        pickle.dump((known_embeddings, known_ids, known_names), f)

    return base_dir / "face_model.pkl"
def main():
    try:
        train_model()
        return 0
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
