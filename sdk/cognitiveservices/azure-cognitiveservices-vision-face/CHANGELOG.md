# Release History

## 0.6.0 (2021-12-02)

**Features**

  - Add support for Face Recognition Quality Score.

**Breaking changes**

  - Various operations that previously accepted an optional name parameter
    are now required.

## 0.5.0 (2021-03-12)

**Features**

  - Model FaceAttributes has a new parameter mask

**Breaking changes**

  - Operation FaceOperations.detect_with_stream has a new signature
  - Operation FaceOperations.detect_with_url has a new signature

## 0.4.1 (2020-06-24)

**Features**

- Add recognition_03 support

## 0.4.0 (2019-06-27)

**Features**

  - Add "detection_model" to operations when possible. This is a
    breaking change if you were using positional arguments on some
    scenarios

**Breaking changes**

  - Operation FaceListOperations.add_face_from_stream has a new
    signature
  - Operation FaceListOperations.add_face_from_url has a new
    signature
  - Operation FaceOperations.detect_with_stream has a new signature
  - Operation FaceOperations.detect_with_url has a new signature
  - Operation LargeFaceListOperations.add_face_from_stream has a new
    signature
  - Operation LargeFaceListOperations.add_face_from_url has a new
    signature
  - Operation LargePersonGroupPersonOperations.add_face_from_stream
    has a new signature
  - Operation LargePersonGroupPersonOperations.add_face_from_url has
    a new signature
  - Operation PersonGroupPersonOperations.add_face_from_stream has a
    new signature
  - Operation PersonGroupPersonOperations.add_face_from_url has a new
    signature

## 0.3.0 (2019-03-28)

**Features**

  - Model PersonGroup has a new parameter recognition_model
  - Model FaceList has a new parameter recognition_model
  - Model LargePersonGroup has a new parameter recognition_model
  - Model LargeFaceList has a new parameter recognition_model
  - Model DetectedFace has a new parameter recognition_model

**Breaking changes**

  - Operation FaceListOperations.create has a new signature
  - Operation FaceListOperations.get has a new signature
  - Operation FaceOperations.detect_with_stream has a new signature
  - Operation FaceOperations.detect_with_stream has a new signature
  - Operation FaceOperations.detect_with_url has a new signature
  - Operation FaceOperations.detect_with_url has a new signature
  - Operation LargeFaceListOperations.create has a new signature
  - Operation LargeFaceListOperations.get has a new signature
  - Operation LargePersonGroupOperations.create has a new signature
  - Operation LargePersonGroupOperations.get has a new signature
  - Operation LargePersonGroupOperations.list has a new signature
  - Operation PersonGroupOperations.create has a new signature
  - Operation PersonGroupOperations.get has a new signature
  - Operation PersonGroupOperations.list has a new signature
  - Operation FaceListOperations.list has a new signature
  - Operation LargeFaceListOperations.list has a new signature

## 0.2.0 (2019-03-07)

  - Add snapshots features

## 0.1.0 (2018-10-17)

  - Initial Release
