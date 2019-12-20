
# Release History

-------------------

## 1.0.0 (Unreleased)

### Features

- Add AAD auth support    #8924

### Breaking changes

- List_configuration_settings & list_revisions now take string key/label filter instead of keys/labels list   #9066

## 1.0.0b6 (2019-12-03)

### Features

- Add sync-token support    #8418

### Breaking changes

- Combine set_read_only & clear_read_only to be set_read_only(True/False)   #8453

## 1.0.0b5 (2019-10-30)

### Breaking changes

- etag and match_condition of delete_configuration_setting are now keyword argument only #8161

## 1.0.0b4 (2019-10-07)

- Add conditional operation support
- Add set_read_only and clear_read_only methods

## 1.0.0b3 (2019-09-09)

- New azure app configuration
