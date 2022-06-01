# @title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Script adapted from: https://github.com/tensorflow/docs/blob/master/site/en/tutorials/distribute/multi_worker_with_keras.ipynb
# =========================================================================

import tensorflow as tf
import numpy as np

import argparse
import os, json


def mnist_dataset(batch_size):
    (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
    # The `x` arrays are in uint8 and have values in the range [0, 255].
    # We need to convert them to float32 with values in the range [0, 1]
    x_train = x_train / np.float32(255)
    y_train = y_train.astype(np.int64)
    train_dataset = (
        tf.data.Dataset.from_tensor_slices((x_train, y_train))
        .shuffle(60000)
        .repeat()
        .batch(batch_size)
    )
    return train_dataset


def build_and_compile_cnn_model():
    model = tf.keras.Sequential(
        [
            tf.keras.Input(shape=(28, 28)),
            tf.keras.layers.Reshape(target_shape=(28, 28, 1)),
            tf.keras.layers.Conv2D(32, 3, activation="relu"),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(10),
        ]
    )
    model.compile(
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.001),
        metrics=["accuracy"],
    )
    return model


def _is_chief(task_type, task_id):
    # If `task_type` is None, this may be operating as single worker, which works
    # effectively as chief.
    return (
        task_type is None
        or task_type == "chief"
        or (task_type == "worker" and task_id == 0)
    )


def _get_temp_dir(dirpath, task_id):
    base_dirpath = "workertemp_" + str(task_id)
    temp_dir = os.path.join(dirpath, base_dirpath)
    tf.io.gfile.makedirs(temp_dir)
    return temp_dir


def write_filepath(filepath, task_type, task_id):
    dirpath = os.path.dirname(filepath)
    base = os.path.basename(filepath)
    if not _is_chief(task_type, task_id):
        dirpath = _get_temp_dir(dirpath, task_id)
    return os.path.join(dirpath, base)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--steps-per-epoch", type=int, default=70)
    parser.add_argument("--per-worker-batch-size", type=int, default=64)
    parser.add_argument(
        "--model-dir",
        type=str,
        default="outputs",
        help="directory to save the model to",
    )

    args = parser.parse_args()

    tf_config = json.loads(os.environ["TF_CONFIG"])
    num_workers = len(tf_config["cluster"]["worker"])

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()

    # Here the batch size scales up by number of workers since
    # `tf.data.Dataset.batch` expects the global batch size.
    global_batch_size = args.per_worker_batch_size * num_workers
    multi_worker_dataset = mnist_dataset(global_batch_size)

    with strategy.scope():
        # Model building/compiling need to be within `strategy.scope()`.
        multi_worker_model = build_and_compile_cnn_model()

    # Keras' `model.fit()` trains the model with specified number of epochs and
    # number of steps per epoch.
    multi_worker_model.fit(
        multi_worker_dataset, epochs=args.epochs, steps_per_epoch=args.steps_per_epoch
    )

    # Save the model
    task_type, task_id = (tf_config["task"]["type"], tf_config["task"]["index"])
    write_model_path = write_filepath(args.model_dir, task_type, task_id)

    multi_worker_model.save(write_model_path)


if __name__ == "__main__":
    main()
