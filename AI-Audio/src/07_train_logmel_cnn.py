# # # # ==========================================================
# # # # Transfer Learning Model (EfficientNetB0)
# # # # ==========================================================

# # # from tensorflow.keras.applications import EfficientNetB0
# # # from tensorflow.keras.layers import (
# # #     Input,
# # #     Conv2D,
# # #     BatchNormalization,
# # #     GlobalAveragePooling2D,
# # #     Dropout,
# # #     Dense
# # # )
# # # from tensorflow.keras.models import Model

# # # # ----------------------------------------------------------
# # # # Convert 1-channel spectrogram to 3-channel
# # # # ----------------------------------------------------------

# # # inputs = Input(shape=(128,128,1))

# # # x = Conv2D(
# # #     3,
# # #     (1,1),
# # #     padding="same",
# # #     activation=None
# # # )(inputs)

# # # # ----------------------------------------------------------
# # # # Pretrained Backbone
# # # # ----------------------------------------------------------

# # # base_model = EfficientNetB0(

# # #     include_top=False,

# # #     weights="imagenet",

# # #     input_tensor=x

# # # )

# # # # Freeze pretrained layers initially

# # # base_model.trainable = False

# # # # ----------------------------------------------------------
# # # # Classification Head
# # # # ----------------------------------------------------------

# # # x = base_model.output

# # # x = GlobalAveragePooling2D()(x)

# # # x = BatchNormalization()(x)

# # # x = Dropout(0.40)(x)

# # # x = Dense(

# # #     512,

# # #     activation="relu",

# # #     kernel_initializer=HeNormal()

# # # )(x)

# # # x = Dropout(0.50)(x)

# # # outputs = Dense(

# # #     NUM_CLASSES,

# # #     activation="softmax"

# # # )(x)

# # # model = Model(inputs, outputs)

# # # # ==========================================================
# # # # Compile
# # # # ==========================================================

# # # model.compile(

# # #     optimizer=tf.keras.optimizers.Adam(

# # #         learning_rate=1e-3

# # #     ),

# # #     loss="sparse_categorical_crossentropy",

# # #     metrics=["accuracy"]

# # # )

# # # print()
# # # model.summary()

# # # # ==========================================================
# # # # Callbacks
# # # # ==========================================================

# # # callbacks = [

# # #     EarlyStopping(

# # #         monitor="val_loss",

# # #         patience=10,

# # #         restore_best_weights=True,

# # #         verbose=1

# # #     ),

# # #     ReduceLROnPlateau(

# # #         monitor="val_loss",

# # #         factor=0.5,

# # #         patience=5,

# # #         min_lr=1e-6,

# # #         verbose=1

# # #     ),

# # #     ModelCheckpoint(

# # #         filepath=MODEL_PATH / "best_logmel_model.keras",

# # #         monitor="val_accuracy",

# # #         save_best_only=True,

# # #         verbose=1

# # #     ),

# # #     CSVLogger(

# # #         LOG_PATH / "training_log.csv"

# # #     )

# # # ]
# # # # ==========================================================
# # # # Train
# # # # ==========================================================

# # # print("\n")
# # # print("="*60)
# # # print("Training Started")
# # # print("="*60)

# # # history = model.fit(

# # #     X_train,

# # #     y_train,

# # #     validation_data=(X_val,y_val),

# # #     epochs=50,

# # #     batch_size=32,

# # #     callbacks=callbacks,

# # #     shuffle=True,

# # #     verbose=1

# # # )
# # # # ==========================================================
# # # # Evaluate
# # # # ==========================================================

# # # print("\n")
# # # print("="*60)
# # # print("Evaluating Model")
# # # print("="*60)

# # # loss, accuracy = model.evaluate(

# # #     X_test,

# # #     y_test,

# # #     verbose=1

# # # )

# # # print()

# # # print("Test Accuracy :",accuracy)

# # # print("Test Loss :",loss)
# # # # ==========================================================
# # # # Save Final Model
# # # # ==========================================================

# # # model.save(

# # #     MODEL_PATH / "final_logmel_model.keras"

# # # )

# # # print()

# # # print("Final model saved.")

# # from pathlib import Path

# # import numpy as np
# # import tensorflow as tf
# # import matplotlib.pyplot as plt
# # import seaborn as sns

# # from sklearn.model_selection import train_test_split
# # from sklearn.metrics import (
# #     confusion_matrix,
# #     classification_report
# # )

# # from tensorflow.keras.models import Model

# # from tensorflow.keras.layers import (
# #     Input,
# #     Conv2D,
# #     Dense,
# #     Dropout,
# #     BatchNormalization,
# #     GlobalAveragePooling2D
# # )

# # from tensorflow.keras.callbacks import (
# #     EarlyStopping,
# #     ReduceLROnPlateau,
# #     ModelCheckpoint,
# #     CSVLogger
# # )

# # from tensorflow.keras.initializers import HeNormal

# # from tensorflow.keras.applications import EfficientNetB0

# # # ==========================================================
# # # Paths
# # # ==========================================================

# # PROJECT_ROOT = Path(__file__).resolve().parent.parent

# # FEATURE_PATH = PROJECT_ROOT / "mel_features"

# # MODEL_PATH = PROJECT_ROOT / "models"
# # MODEL_PATH.mkdir(exist_ok=True)

# # LOG_PATH = PROJECT_ROOT / "logs"
# # LOG_PATH.mkdir(exist_ok=True)

# # PLOT_PATH = PROJECT_ROOT / "plots"
# # PLOT_PATH.mkdir(exist_ok=True)

# # RESULT_PATH = PROJECT_ROOT / "results"
# # RESULT_PATH.mkdir(exist_ok=True)

# # # ==========================================================
# # # Load Dataset
# # # ==========================================================

# # print("="*60)
# # print("Loading Log-Mel Dataset")
# # print("="*60)

# # X = np.load(FEATURE_PATH / "X_logmel.npy")
# # y = np.load(FEATURE_PATH / "y_logmel.npy")

# # print("X Shape :", X.shape)
# # print("y Shape :", y.shape)

# # NUM_CLASSES = len(np.unique(y))

# # # ==========================================================
# # # Split Dataset
# # # ==========================================================

# # X_train, X_temp, y_train, y_temp = train_test_split(

# #     X,
# #     y,

# #     test_size=0.20,

# #     random_state=42,

# #     stratify=y

# # )

# # X_val, X_test, y_val, y_test = train_test_split(

# #     X_temp,
# #     y_temp,

# #     test_size=0.50,

# #     random_state=42,

# #     stratify=y_temp

# # )

# # print()

# # print("Training   :", X_train.shape)
# # print("Validation :", X_val.shape)
# # print("Testing    :", X_test.shape)

# # # ==========================================================
# # # EfficientNetB0 Model
# # # ==========================================================

# # inputs = Input(shape=(128,128,1))

# # # Convert grayscale to RGB

# # x = Conv2D(

# #     filters=3,

# #     kernel_size=(1,1),

# #     padding="same",

# #     activation=None

# # )(inputs)

# # # ==========================================================
# # # Pretrained Backbone
# # # ==========================================================

# # base_model = EfficientNetB0(

# #     include_top=False,

# #     weights="imagenet",

# #     input_tensor=x

# # )

# # # Freeze all EfficientNet layers

# # base_model.trainable = False

# # # ==========================================================
# # # Classification Head
# # # ==========================================================

# # x = base_model.output

# # x = GlobalAveragePooling2D()(x)

# # x = BatchNormalization()(x)

# # x = Dropout(0.40)(x)

# # x = Dense(

# #     512,

# #     activation="relu",

# #     kernel_initializer=HeNormal()

# # )(x)

# # x = Dropout(0.50)(x)

# # outputs = Dense(

# #     NUM_CLASSES,

# #     activation="softmax"

# # )(x)

# # model = Model(

# #     inputs,

# #     outputs

# # )

# # # ==========================================================
# # # Compile
# # # ==========================================================

# # model.compile(

# #     optimizer=tf.keras.optimizers.Adam(

# #         learning_rate=1e-3

# #     ),

# #     loss="sparse_categorical_crossentropy",

# #     metrics=["accuracy"]

# # )

# # print()

# # model.summary()

# # # ==========================================================
# # # Callbacks
# # # ==========================================================

# # callbacks = [

# #     EarlyStopping(

# #         monitor="val_loss",

# #         patience=8,

# #         restore_best_weights=True,

# #         verbose=1

# #     ),

# #     ReduceLROnPlateau(

# #         monitor="val_loss",

# #         factor=0.5,

# #         patience=3,

# #         min_lr=1e-6,

# #         verbose=1

# #     ),

# #     ModelCheckpoint(

# #         filepath=MODEL_PATH / "best_logmel_model.keras",

# #         monitor="val_accuracy",

# #         save_best_only=True,

# #         verbose=1

# #     ),

# #     CSVLogger(

# #         LOG_PATH / "training_log.csv"

# #     )

# # ]

# # # ==========================================================
# # # Phase 1 Training
# # # Train only the classifier head
# # # ==========================================================

# # print()
# # print("="*60)
# # print("PHASE 1 : Training Classification Head")
# # print("="*60)

# # history_phase1 = model.fit(

# #     X_train,

# #     y_train,

# #     validation_data=(X_val, y_val),

# #     epochs=15,

# #     batch_size=32,

# #     callbacks=callbacks,

# #     shuffle=True,

# #     verbose=1

# # )

# # # ==========================================================
# # # Phase 2
# # # Fine Tune EfficientNet
# # # ==========================================================

# # print()
# # print("="*60)
# # print("PHASE 2 : Fine Tuning EfficientNet")
# # print("="*60)

# # # Unfreeze the backbone

# # base_model.trainable = True

# # # Freeze the earlier layers
# # # Train only the last ~30 layers

# # for layer in base_model.layers[:-30]:

# #     layer.trainable = False

# # print()

# # print("Trainable Layers:")

# # count = 0

# # for layer in model.layers:

# #     if layer.trainable:

# #         count += 1
# #         print(layer.name)

# # print()

# # print("Total Trainable Layers :", count)

# # # ==========================================================
# # # Recompile with lower learning rate
# # # ==========================================================

# # model.compile(

# #     optimizer=tf.keras.optimizers.Adam(

# #         learning_rate=1e-5

# #     ),

# #     loss="sparse_categorical_crossentropy",

# #     metrics=["accuracy"]

# # )

# # # ==========================================================
# # # Fine Tune
# # # ==========================================================

# # history_phase2 = model.fit(

# #     X_train,

# #     y_train,

# #     validation_data=(X_val, y_val),

# #     epochs=20,

# #     batch_size=16,

# #     callbacks=callbacks,

# #     shuffle=True,

# #     verbose=1

# # )

# # print()
# # print("="*60)
# # print("Training Completed")
# # print("="*60) 
# # # ==========================================================
# # # Evaluate Model
# # # ==========================================================

# # print()
# # print("="*60)
# # print("Evaluating Model")
# # print("="*60)

# # loss, accuracy = model.evaluate(

# #     X_test,

# #     y_test,

# #     verbose=1

# # )

# # print()

# # print(f"Test Accuracy : {accuracy:.4f}")

# # print(f"Test Loss     : {loss:.4f}")

# # # ==========================================================
# # # Save Final Model
# # # ==========================================================

# # model.save(

# #     MODEL_PATH / "final_logmel_model.keras"

# # )

# # print()

# # print("Final Model Saved Successfully")

# # # ==========================================================
# # # Predictions
# # # ==========================================================

# # print()
# # print("="*60)
# # print("Generating Predictions")
# # print("="*60)

# # y_pred_prob = model.predict(

# #     X_test,

# #     verbose=1

# # )

# # y_pred = np.argmax(

# #     y_pred_prob,

# #     axis=1

# # )

# # # ==========================================================
# # # Classification Report
# # # ==========================================================

# # report = classification_report(

# #     y_test,

# #     y_pred,

# #     digits=4

# # )

# # print()

# # print(report)

# # with open(

# #     RESULT_PATH / "classification_report.txt",

# #     "w"

# # ) as f:

# #     f.write(report)

# # print("Classification Report Saved")

# # # ==========================================================
# # # Confusion Matrix
# # # ==========================================================

# # cm = confusion_matrix(

# #     y_test,

# #     y_pred

# # )

# # plt.figure(

# #     figsize=(15,12)

# # )

# # sns.heatmap(

# #     cm,

# #     cmap="Blues",

# #     square=True,

# #     cbar=True

# # )

# # plt.title(

# #     "Confusion Matrix"

# # )

# # plt.xlabel(

# #     "Predicted"

# # )

# # plt.ylabel(

# #     "Actual"

# # )

# # plt.tight_layout()

# # plt.savefig(

# #     PLOT_PATH / "confusion_matrix.png",

# #     dpi=300

# # )

# # plt.close()

# # print("Confusion Matrix Saved")

# # # ==========================================================
# # # Combine Training History
# # # ==========================================================

# # history = {}

# # for key in history_phase1.history.keys():

# #     history[key] = (

# #         history_phase1.history[key]

# #         +

# #         history_phase2.history[key]

# #     )

# # # ==========================================================
# # # Accuracy Graph
# # # ==========================================================

# # plt.figure(

# #     figsize=(10,5)

# # )

# # plt.plot(

# #     history["accuracy"],

# #     label="Training Accuracy",

# #     linewidth=2

# # )

# # plt.plot(

# #     history["val_accuracy"],

# #     label="Validation Accuracy",

# #     linewidth=2

# # )

# # plt.xlabel("Epoch")

# # plt.ylabel("Accuracy")

# # plt.title("Training vs Validation Accuracy")

# # plt.legend()

# # plt.grid(True)

# # plt.tight_layout()

# # plt.savefig(

# #     PLOT_PATH / "accuracy_curve.png",

# #     dpi=300

# # )

# # plt.close()

# # print("Accuracy Graph Saved")

# # # ==========================================================
# # # Loss Graph
# # # ==========================================================

# # plt.figure(

# #     figsize=(10,5)

# # )

# # plt.plot(

# #     history["loss"],

# #     label="Training Loss",

# #     linewidth=2

# # )

# # plt.plot(

# #     history["val_loss"],

# #     label="Validation Loss",

# #     linewidth=2

# # )

# # plt.xlabel("Epoch")

# # plt.ylabel("Loss")

# # plt.title("Training vs Validation Loss")

# # plt.legend()

# # plt.grid(True)

# # plt.tight_layout()

# # plt.savefig(

# #     PLOT_PATH / "loss_curve.png",

# #     dpi=300

# # )

# # plt.close()

# # print("Loss Graph Saved")

# # # ==========================================================
# # # Finish
# # # ==========================================================

# # print()
# # print("="*60)
# # print("Training Pipeline Completed Successfully")
# # print("="*60)

# # print()

# # print("Saved Files")

# # print("-------------------------------")

# # print("Model                :", MODEL_PATH)

# # print("Training Log         :", LOG_PATH)

# # print("Plots                :", PLOT_PATH)

# # print("Results              :", RESULT_PATH)
# # # ==========================================================
# # # Save Label Mapping
# # # ==========================================================

# # import pandas as pd
# # from pathlib import Path

# # CSV_PATH = (
# #     PROJECT_ROOT /
# #     "datasets" /
# #     "ESC-50" /
# #     "meta" /
# #     "esc50.csv"
# # )

# # df = pd.read_csv(CSV_PATH)

# # labels = (
# #     df[["target", "category"]]
# #     .drop_duplicates()
# #     .sort_values("target")
# # )

# # labels.to_csv(

# #     RESULT_PATH / "label_mapping.csv",

# #     index=False

# # )

# # print("Label Mapping Saved")

# # # ==========================================================
# # # Save Model Summary
# # # ==========================================================

# # with open(

# #     RESULT_PATH / "model_summary.txt",

# #     "w"

# # ) as f:

# #     model.summary(

# #         print_fn=lambda x: f.write(x + "\n")

# #     )

# # print("Model Summary Saved")

# # # ==========================================================
# # # Save Training History
# # # ==========================================================

# # history_df = pd.DataFrame(history)

# # history_df.to_csv(

# #     RESULT_PATH / "training_history.csv",

# #     index=False

# # )

# # print("Training History Saved")

# # # ==========================================================
# # # Save Sample Prediction
# # # ==========================================================

# # sample = np.expand_dims(

# #     X_test[0],

# #     axis=0

# # )

# # prediction = model.predict(

# #     sample,

# #     verbose=0

# # )

# # predicted = np.argmax(prediction)

# # actual = y_test[0]

# # confidence = float(np.max(prediction))

# # with open(

# #     RESULT_PATH / "sample_prediction.txt",

# #     "w"

# # ) as f:

# #     f.write("Sample Prediction\n")

# #     f.write("=========================\n\n")

# #     f.write(f"Actual Label    : {actual}\n")

# #     f.write(f"Predicted Label : {predicted}\n")

# #     f.write(f"Confidence      : {confidence:.4f}\n")

# # print("Sample Prediction Saved")

# # # ==========================================================
# # # Save Complete Metrics
# # # ==========================================================

# # with open(

# #     RESULT_PATH / "metrics.txt",

# #     "w"

# # ) as f:

# #     f.write("Model Evaluation\n")

# #     f.write("============================\n\n")

# #     f.write(f"Test Accuracy : {accuracy:.4f}\n")

# #     f.write(f"Test Loss     : {loss:.4f}\n")

# # print("Metrics Saved")

# # # ==========================================================
# # # Finished
# # # ==========================================================

# # print()

# # print("="*70)
# # print("ALL FILES GENERATED SUCCESSFULLY")
# # print("="*70)

# # print()

# # print("Generated Files")

# # print("---------------------------------------")

# # print("✔ final_logmel_model.keras")

# # print("✔ best_logmel_model.keras")

# # print("✔ training_log.csv")

# # print("✔ training_history.csv")

# # print("✔ classification_report.txt")

# # print("✔ confusion_matrix.png")

# # print("✔ accuracy_curve.png")

# # print("✔ loss_curve.png")

# # print("✔ label_mapping.csv")

# # print("✔ model_summary.txt")

# # print("✔ metrics.txt")

# # print("✔ sample_prediction.txt")

# # print()

# # print("="*70)
# # print("Module 7 Completed Successfully")
# # print("="*70)

# from pathlib import Path

# import numpy as np
# import tensorflow as tf
# import matplotlib.pyplot as plt
# import seaborn as sns

# from sklearn.model_selection import train_test_split
# from sklearn.metrics import (
#     confusion_matrix,
#     classification_report
# )

# from tensorflow.keras.models import Model

# from tensorflow.keras.layers import (
#     Input,
#     Conv2D,
#     Dense,
#     Dropout,
#     BatchNormalization,
#     GlobalAveragePooling2D,
#     Concatenate
# )

# from tensorflow.keras.callbacks import (
#     EarlyStopping,
#     ReduceLROnPlateau,
#     ModelCheckpoint,
#     CSVLogger
# )

# from tensorflow.keras.initializers import HeNormal

# from tensorflow.keras.applications import EfficientNetB0
# # ==========================================================
# # Paths
# # ==========================================================

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# FEATURE_PATH = PROJECT_ROOT / "mel_features"

# MODEL_PATH = PROJECT_ROOT / "models"
# MODEL_PATH.mkdir(exist_ok=True)

# LOG_PATH = PROJECT_ROOT / "logs"
# LOG_PATH.mkdir(exist_ok=True)

# PLOT_PATH = PROJECT_ROOT / "plots"
# PLOT_PATH.mkdir(exist_ok=True)

# RESULT_PATH = PROJECT_ROOT / "results"
# RESULT_PATH.mkdir(exist_ok=True)
# # ==========================================================
# # Load Dataset
# # ==========================================================

# print("="*60)
# print("Loading Log-Mel Dataset")
# print("="*60)

# X = np.load(FEATURE_PATH / "X_logmel.npy")
# y = np.load(FEATURE_PATH / "y_logmel.npy")

# print("X Shape :", X.shape)
# print("y Shape :", y.shape)

# NUM_CLASSES = len(np.unique(y))
# # ==========================================================
# # Dataset Split
# # ==========================================================

# X_train, X_temp, y_train, y_temp = train_test_split(

#     X,
#     y,

#     test_size=0.20,

#     random_state=42,

#     stratify=y

# )

# X_val, X_test, y_val, y_test = train_test_split(

#     X_temp,
#     y_temp,

#     test_size=0.50,

#     random_state=42,

#     stratify=y_temp

# )

# print()
# print("Training   :", X_train.shape)
# print("Validation :", X_val.shape)
# print("Testing    :", X_test.shape)
# # ==========================================================
# # EfficientNetB0 Transfer Learning Model
# # ==========================================================

# print()
# print("="*60)
# print("Building EfficientNetB0 Model")
# print("="*60)

# # Input (128 x 128 x 1)
# inputs = Input(shape=(128, 128, 1))

# # ----------------------------------------------------------
# # Convert grayscale spectrogram to RGB
# # ----------------------------------------------------------

# x = Concatenate()([inputs, inputs, inputs])

# # ----------------------------------------------------------
# # Load EfficientNetB0
# # ----------------------------------------------------------

# base_model = EfficientNetB0(

#     include_top=False,

#     weights="imagenet",

#     input_shape=(128,128,3)

# )

# # Freeze pretrained layers
# base_model.trainable = False

# # ----------------------------------------------------------
# # Forward Pass
# # ----------------------------------------------------------

# x = base_model(x, training=False)

# # ----------------------------------------------------------
# # Classification Head
# # ----------------------------------------------------------

# x = GlobalAveragePooling2D()(x)

# x = BatchNormalization()(x)

# x = Dropout(0.40)(x)

# x = Dense(

#     512,

#     activation="relu",

#     kernel_initializer=HeNormal()

# )(x)

# x = Dropout(0.50)(x)

# outputs = Dense(

#     NUM_CLASSES,

#     activation="softmax"

# )(x)

# model = Model(inputs, outputs)

# print()
# model.summary()

# # ==========================================================
# # Compile Model
# # ==========================================================

# model.compile(

#     optimizer=tf.keras.optimizers.Adam(

#         learning_rate=1e-3

#     ),

#     loss="sparse_categorical_crossentropy",

#     metrics=["accuracy"]

# )
# # ==========================================================
# # Callbacks
# # ==========================================================

# callbacks = [

#     EarlyStopping(

#         monitor="val_loss",

#         patience=8,

#         restore_best_weights=True,

#         verbose=1

#     ),

#     ReduceLROnPlateau(

#         monitor="val_loss",

#         factor=0.5,

#         patience=3,

#         min_lr=1e-6,

#         verbose=1

#     ),

#     ModelCheckpoint(

#         filepath=MODEL_PATH / "best_logmel_model.keras",

#         monitor="val_accuracy",

#         save_best_only=True,

#         verbose=1

#     ),

#     CSVLogger(

#         LOG_PATH / "training_log.csv"

#     )

# ]
# # ==========================================================
# # Phase 1 : Train Classification Head
# # ==========================================================

# print()
# print("="*60)
# print("PHASE 1 : Training Classification Head")
# print("="*60)

# history_phase1 = model.fit(

#     X_train,

#     y_train,

#     validation_data=(X_val, y_val),

#     epochs=15,

#     batch_size=32,

#     callbacks=callbacks,

#     shuffle=True,

#     verbose=1

# )
# # ==========================================================
# # Phase 2 : Fine Tune EfficientNet
# # ==========================================================

# print()
# print("="*60)
# print("PHASE 2 : Fine Tuning")
# print("="*60)

# # Unfreeze backbone

# base_model.trainable = True
# # Freeze earlier layers

# for layer in base_model.layers[:-30]:

#     layer.trainable = False
# print()
# print("Trainable Layers")

# count = 0

# for layer in base_model.layers:

#     if layer.trainable:

#         count += 1

# print("Total Trainable Layers :", count)
# # ==========================================================
# # Recompile
# # ==========================================================

# model.compile(

#     optimizer=tf.keras.optimizers.Adam(

#         learning_rate=1e-5

#     ),

#     loss="sparse_categorical_crossentropy",

#     metrics=["accuracy"]

# )
# # ==========================================================
# # Fine Tune Training
# # ==========================================================

# history_phase2 = model.fit(

#     X_train,

#     y_train,

#     validation_data=(X_val, y_val),

#     epochs=20,

#     batch_size=16,

#     callbacks=callbacks,

#     shuffle=True,

#     verbose=1

# )
# print()
# print("="*60)
# print("Training Completed")
# print("="*60)
# # ==========================================================
# # Callbacks
# # ==========================================================

# callbacks = [

#     EarlyStopping(

#         monitor="val_loss",

#         patience=10,

#         restore_best_weights=True,

#         verbose=1

#     ),

#     ReduceLROnPlateau(

#         monitor="val_loss",

#         factor=0.5,

#         patience=4,

#         min_lr=1e-6,

#         verbose=1

#     ),

#     ModelCheckpoint(

#         filepath=MODEL_PATH / "best_logmel_model.keras",

#         monitor="val_accuracy",

#         save_best_only=True,

#         verbose=1

#     ),

#     CSVLogger(

#         LOG_PATH / "training_log.csv"

#     )

# ]
# print("\n")
# print("="*60)
# print("Stage 1 : Training Classification Head")
# print("="*60)

# history1 = model.fit(

#     X_train,

#     y_train,

#     validation_data=(X_val, y_val),

#     epochs=15,

#     batch_size=32,

#     callbacks=callbacks,

#     shuffle=True,

#     verbose=1

# )
# print("\n")
# print("="*60)
# print("Stage 2 : Fine-Tuning Entire EfficientNet")
# print("="*60)

# base_model.trainable = True

# model.compile(

#     optimizer=tf.keras.optimizers.Adam(

#         learning_rate=1e-5

#     ),

#     loss="sparse_categorical_crossentropy",

#     metrics=["accuracy"]

# )

# history2 = model.fit(

#     X_train,

#     y_train,

#     validation_data=(X_val, y_val),

#     epochs=35,

#     batch_size=32,

#     callbacks=callbacks,

#     shuffle=True,

#     verbose=1

# )
# print("\n")
# print("="*60)
# print("Evaluating Model")
# print("="*60)

# loss, accuracy = model.evaluate(

#     X_test,

#     y_test,

#     verbose=1

# )

# print()

# print(f"Test Accuracy : {accuracy:.4f}")

# print(f"Test Loss     : {loss:.4f}")
# predictions = model.predict(X_test)

# y_pred = np.argmax(predictions, axis=1)
# print("\n")
# print("="*60)
# print("Classification Report")
# print("="*60)

# report = classification_report(

#     y_test,

#     y_pred,

#     digits=4

# )

# print(report)

# with open(

#     RESULT_PATH / "classification_report.txt",

#     "w"

# ) as f:

#     f.write(report)
# cm = confusion_matrix(

#     y_test,

#     y_pred

# )

# plt.figure(figsize=(12,10))

# sns.heatmap(

#     cm,

#     cmap="Blues"

# )

# plt.title("Confusion Matrix")

# plt.xlabel("Predicted")

# plt.ylabel("Actual")

# plt.tight_layout()

# plt.savefig(

#     PLOT_PATH / "confusion_matrix.png"

# )

# plt.close()
# plt.figure(figsize=(8,5))

# train_acc = history1.history["accuracy"] + history2.history["accuracy"]

# val_acc = history1.history["val_accuracy"] + history2.history["val_accuracy"]

# plt.plot(train_acc,label="Train")

# plt.plot(val_acc,label="Validation")

# plt.xlabel("Epoch")

# plt.ylabel("Accuracy")

# plt.title("Training Accuracy")

# plt.legend()

# plt.grid(True)

# plt.savefig(

#     PLOT_PATH / "accuracy.png"

# )

# plt.close()
# plt.figure(figsize=(8,5))

# train_loss = history1.history["loss"] + history2.history["loss"]

# val_loss = history1.history["val_loss"] + history2.history["val_loss"]

# plt.plot(train_loss,label="Train")

# plt.plot(val_loss,label="Validation")

# plt.xlabel("Epoch")

# plt.ylabel("Loss")

# plt.title("Training Loss")

# plt.legend()

# plt.grid(True)

# plt.savefig(

#     PLOT_PATH / "loss.png"

# )

# plt.close()
# model.save(

#     MODEL_PATH / "final_logmel_model.keras"

# )

# print()

# print("="*60)
# print("Training Complete")
# print("="*60)

# print("Model Saved")

# print("Graphs Saved")

# print("Classification Report Saved")

# print("Confusion Matrix Saved")

from pathlib import Path

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    classification_report
)

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import (
    Input,
    Conv2D,
    MaxPooling2D,
    BatchNormalization,
    Dropout,
    Dense,
    GlobalAveragePooling2D
)

from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
    CSVLogger
)

from tensorflow.keras.regularizers import l2
from tensorflow.keras.initializers import HeNormal

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FEATURE_PATH = PROJECT_ROOT / "mel_features"

MODEL_PATH = PROJECT_ROOT / "models"
MODEL_PATH.mkdir(exist_ok=True)

LOG_PATH = PROJECT_ROOT / "logs"
LOG_PATH.mkdir(exist_ok=True)

PLOT_PATH = PROJECT_ROOT / "plots"
PLOT_PATH.mkdir(exist_ok=True)

RESULT_PATH = PROJECT_ROOT / "results"
RESULT_PATH.mkdir(exist_ok=True)

# ==========================================================
# Load Dataset
# ==========================================================

print("=" * 60)
print("Loading Log-Mel Dataset")
print("=" * 60)

X = np.load(FEATURE_PATH / "X_logmel.npy")
y = np.load(FEATURE_PATH / "y_logmel.npy")

print("X Shape :", X.shape)
print("y Shape :", y.shape)

NUM_CLASSES = len(np.unique(y))
# ==========================================================
# Train / Validation / Test Split
# ==========================================================

X_train, X_temp, y_train, y_temp = train_test_split(

    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y

)

X_val, X_test, y_val, y_test = train_test_split(

    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp

)

print()
print("=" * 60)
print("Dataset Split")
print("=" * 60)

print("Training   :", X_train.shape)
print("Validation :", X_val.shape)
print("Testing    :", X_test.shape)

print()

print("Training Samples   :", len(X_train))
print("Validation Samples :", len(X_val))
print("Testing Samples    :", len(X_test))

print()

print("Number of Classes :", NUM_CLASSES)

# ==========================================================
# Dataset Information
# ==========================================================

print()
print("=" * 60)
print("Dataset Statistics")
print("=" * 60)

print("Input Shape :", X_train.shape[1:])

print("Data Type   :", X_train.dtype)

print("Minimum     :", np.min(X_train))

print("Maximum     :", np.max(X_train))

print("Mean        :", np.mean(X_train))

print("Std         :", np.std(X_train))

# ==========================================================
# Shuffle Training Set
# ==========================================================

shuffle_index = np.random.permutation(len(X_train))

X_train = X_train[shuffle_index]

y_train = y_train[shuffle_index]

print()
print("Training data shuffled successfully.")

# ==========================================================
# Ready for CNN Model
# ==========================================================

print()
print("=" * 60)
print("Preparing CNN Model")
print("=" * 60)
# ==========================================================
# CNN Model
# ==========================================================

print()
print("=" * 60)
print("Building CNN Model")
print("=" * 60)

model = Sequential([

    # ------------------------------------------------------
    # Input
    # ------------------------------------------------------

    Input(shape=(128, 128, 1)),


    # ======================================================
    # Block 1
    # ======================================================

    Conv2D(

        filters=32,

        kernel_size=(3,3),

        padding="same",

        activation="relu",

        kernel_initializer=HeNormal(),

        kernel_regularizer=l2(1e-4)

    ),

    BatchNormalization(),

    MaxPooling2D(pool_size=(2,2)),

    Dropout(0.25),


    # ======================================================
    # Block 2
    # ======================================================

    Conv2D(

        filters=64,

        kernel_size=(3,3),

        padding="same",

        activation="relu",

        kernel_initializer=HeNormal(),

        kernel_regularizer=l2(1e-4)

    ),

    BatchNormalization(),

    MaxPooling2D(pool_size=(2,2)),

    Dropout(0.30),


    # ======================================================
    # Block 3
    # ======================================================

    Conv2D(

        filters=128,

        kernel_size=(3,3),

        padding="same",

        activation="relu",

        kernel_initializer=HeNormal(),

        kernel_regularizer=l2(1e-4)

    ),

    BatchNormalization(),

    MaxPooling2D(pool_size=(2,2)),

    Dropout(0.35),


    # ======================================================
    # Block 4
    # ======================================================

    Conv2D(

        filters=256,

        kernel_size=(3,3),

        padding="same",

        activation="relu",

        kernel_initializer=HeNormal(),

        kernel_regularizer=l2(1e-4)

    ),

    BatchNormalization(),

    MaxPooling2D(pool_size=(2,2)),

    Dropout(0.40),


    # ======================================================
    # Feature Compression
    # ======================================================

    GlobalAveragePooling2D(),


    # ======================================================
    # Dense Layer
    # ======================================================

    Dense(

        256,

        activation="relu",

        kernel_initializer=HeNormal()

    ),

    Dropout(0.50),


    # ======================================================
    # Output Layer
    # ======================================================

    Dense(

        NUM_CLASSES,

        activation="softmax"

    )

])

print()

model.summary()
# ==========================================================
# Compile Model
# ==========================================================

print()
print("=" * 60)
print("Compiling Model")
print("=" * 60)

model.compile(

    optimizer=tf.keras.optimizers.Adam(

        learning_rate=0.001

    ),

    loss="sparse_categorical_crossentropy",

    metrics=["accuracy"]

)

# ==========================================================
# Callbacks
# ==========================================================

callbacks = [

    EarlyStopping(

        monitor="val_loss",

        patience=10,

        restore_best_weights=True,

        verbose=1

    ),

    ReduceLROnPlateau(

        monitor="val_loss",

        factor=0.5,

        patience=5,

        min_lr=1e-6,

        verbose=1

    ),

    ModelCheckpoint(

        filepath=MODEL_PATH / "best_logmel_model.keras",

        monitor="val_accuracy",

        save_best_only=True,

        verbose=1

    ),

    CSVLogger(

        LOG_PATH / "training_log.csv"

    )

]

# ==========================================================
# Train Model
# ==========================================================

print()
print("=" * 60)
print("Training Started")
print("=" * 60)

history = model.fit(

    X_train,

    y_train,

    validation_data=(X_val, y_val),

    epochs=100,

    batch_size=32,

    callbacks=callbacks,

    shuffle=True,

    verbose=1

)

print()
print("=" * 60)
print("Training Completed")
print("=" * 60)
# ==========================================================
# Evaluate Model
# ==========================================================

print()
print("=" * 60)
print("Evaluating Model")
print("=" * 60)

loss, accuracy = model.evaluate(

    X_test,

    y_test,

    verbose=1

)

print()

print(f"Test Accuracy : {accuracy:.4f}")

print(f"Test Loss     : {loss:.4f}")

# ==========================================================
# Predictions
# ==========================================================

print()
print("=" * 60)
print("Generating Predictions")
print("=" * 60)

predictions = model.predict(

    X_test,

    verbose=1

)

y_pred = np.argmax(

    predictions,

    axis=1

)

# ==========================================================
# Classification Report
# ==========================================================

print()
print("=" * 60)
print("Classification Report")
print("=" * 60)

report = classification_report(

    y_test,

    y_pred,

    digits=4,

    zero_division=0

)

print(report)

with open(

    RESULT_PATH / "classification_report.txt",

    "w"

) as file:

    file.write(report)

# ==========================================================
# Confusion Matrix
# ==========================================================

cm = confusion_matrix(

    y_test,

    y_pred

)

plt.figure(figsize=(12,10))

sns.heatmap(

    cm,

    cmap="Blues"

)

plt.title("Confusion Matrix")

plt.xlabel("Predicted")

plt.ylabel("Actual")

plt.tight_layout()

plt.savefig(

    PLOT_PATH / "confusion_matrix.png"

)

plt.close()

print("Confusion Matrix Saved")

# ==========================================================
# Accuracy Graph
# ==========================================================

plt.figure(figsize=(8,5))

plt.plot(

    history.history["accuracy"],

    label="Training Accuracy"

)

plt.plot(

    history.history["val_accuracy"],

    label="Validation Accuracy"

)

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.title("Training Accuracy")

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(

    PLOT_PATH / "accuracy.png"

)

plt.close()

print("Accuracy Graph Saved")

# ==========================================================
# Loss Graph
# ==========================================================

plt.figure(figsize=(8,5))

plt.plot(

    history.history["loss"],

    label="Training Loss"

)

plt.plot(

    history.history["val_loss"],

    label="Validation Loss"

)

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.title("Training Loss")

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(

    PLOT_PATH / "loss.png"

)

plt.close()

print("Loss Graph Saved")
# ==========================================================
# Save Final Model
# ==========================================================

print()
print("=" * 60)
print("Saving Final Model")
print("=" * 60)

model.save(

    MODEL_PATH / "final_logmel_model.keras"

)

print("Final Model Saved")

# ==========================================================
# Save Labels
# ==========================================================

labels = np.unique(y)

np.save(

    MODEL_PATH / "class_labels.npy",

    labels

)

print("Class Labels Saved")

# ==========================================================
# Final Summary
# ==========================================================

print()
print("=" * 60)
print("Training Summary")
print("=" * 60)

print(f"Training Samples   : {len(X_train)}")
print(f"Validation Samples : {len(X_val)}")
print(f"Testing Samples    : {len(X_test)}")

print()

print(f"Number of Classes  : {NUM_CLASSES}")

print()

print(f"Final Test Accuracy : {accuracy:.4f}")

print(f"Final Test Loss     : {loss:.4f}")

print()

print("Saved Files")

print("------------")

print("Model                :", MODEL_PATH / "final_logmel_model.keras")

print("Best Model           :", MODEL_PATH / "best_logmel_model.keras")

print("Class Labels         :", MODEL_PATH / "class_labels.npy")

print("Training Log         :", LOG_PATH / "training_log.csv")

print("Accuracy Plot        :", PLOT_PATH / "accuracy.png")

print("Loss Plot            :", PLOT_PATH / "loss.png")

print("Confusion Matrix     :", PLOT_PATH / "confusion_matrix.png")

print("Classification Report:", RESULT_PATH / "classification_report.txt")

print()

print("=" * 60)
print("Module 7 Completed Successfully")
print("=" * 60)