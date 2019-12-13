
# Release History

-------------------

## 2020-01-xx Version 1.0.0

### Features

- Add AAD auth support    #8924

### Breaking changes

- List_configuration_settings & list_revisions now take string key/label filter instead of keys/labels list   #9066

## 2019-12-03 Version 1.0.0b6

### Features

- Add sync-token support    #8418

### Breaking changes

- Combine set_read_only & clear_read_only to be set_read_only(True/False)   #8453

## 2019-10-30 Version 1.0.0b5

### Breaking changes

- etag and match_condition of delete_configuration_setting are now keyword argument only #8161

## 2019-10-07 Version 1.0.0b4

- Add conditional operation support
- Add set_read_only and clear_read_only methods

## 2019-09-09 Version 1.0.0b3

- New azure app configuration
