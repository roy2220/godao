# Godao

DAO (Data Access Object) Generation for Go

## Requirements

- python 2/3

## Installation

```bash
pip install -U git+https://github.com/let-z-go/godao
```

## Quick Start

1. Define DAO with YAML (`sample.yaml`):

   ```yaml
   package_name: main

   imports:
       - errors

   $UserDAO:
     strings:
       $TableUserInfo:
         value: user_info

       $TableUserInfoX:
         maker_func_name: LocateUserInfoTable

     $AddUserInfo:
       input:
         $uid: int64
         $nickname: string
         $gender: int8
       output:
         as_result: last_insert_id
       sql: |
         INSERT INTO
           `%s#{str:TableUserInfo}` (`uid`, `nickname`, `gender`)
         VALUES
           (?#{in:uid}, ?#{in:nickname}, ?#{in:gender})

     $GetUserInfo:
       input:
         $uid: int64
       output: &user_info_struct
         $UID: int64
         $Nickname: string
         $Gender: int8
         struct_type_name: UserInfo
         ignore_no_rows: true
       sql: |
         SELECT
           `uid#{out:UID}`, `nickname#{out:Nickname}`, `gender#{out:Gender}`
         FROM
           `%s#{str:TableUserInfo}`
         WHERE
           `uid` = ?#{in:uid}

     $SetUserInfo:
       input:
         $uid: int64
         $args:
           $Nickname: string*
           $Gender: int8*
           struct_type_name: SetUserInfoArgs
       output:
         as_result: rows_affected
       sql: |
         UPDATE
           `%s#{str:TableUserInfo}`
         SET
         #if args.Nickname.Valid || args.Gender.Valid
         #  if args.Nickname.Valid
           `nickname` = ?#{in:args.Nickname},
         #  endif
         #  if args.Gender.Valid
           `gender` = ?#{in:args.Gender},
         #  endif
         #  trim-suffix ,
         #else
         #  error errors.New("invalid args")
         #endif
         WHERE
           `uid` = ?#{in:uid}

     $AddMultiUserInfos:
       input:
         $appID: string
         $argsList:
             $UID: int64
             $Nickname: string
             $Gender: int8
             struct_type_name: AddUserInfoArgs
             is_array: true
       sql: |
         #if len(argsList) == 0
         #  error errors.New("invalid argsList")
         #endif
         INSERT INTO
           `%s#{str:TableUserInfoX(appID)}` (`uid`, `nickname`, `gender`)
         VALUES
         #for i := range argsList
         #  if i >= 1
           ,
         #  endif
           (?#{in:argsList[i].UID}, ?#{in:argsList[i].Nickname}, ?#{in:argsList[i].Gender})
         #endfor

     $GetMultiUserInfos:
       input:
         $appID: string
         $uids: int64[]
       output:
         <<: *user_info_struct
         is_array: true
       sql: |
         SELECT
           `uid#{out:UID}`, `nickname#{out:Nickname}`, `gender#{out:Gender}`
         FROM
           `%s#{str:TableUserInfoX(appID)}`
         WHERE
           `uid` IN (?#{in:uids})

     $GetNicknameOfUserInfo:
       input:
         $appID: string
         $uid: int64
       output:
         $nickname: string
       sql: |
         SELECT
           `nickname#{out:nickname}`
         FROM
           `%s#{str:TableUserInfoX(appID)}`
         WHERE
           `uid` = ?#{in:uid}

     $GetColumnsOfUserInfo:
       input:
         $appID: string
         $uid: int64
         $args:
           $GetNickname: bool
           $GetGender: bool
           struct_type_name: UserInfoColumns
       output:
         <<: *user_info_struct
       sql: |
         #if !(args.GetNickname || args.GetGender)
         #  error errors.New("invalid args")
         #endif
         SELECT
         #if false
           `uid#{out:UID}`,
         #endif
         #if args.GetNickname
           `nickname#{out:Nickname}`,
         #endif
         #if args.GetGender
           `gender#{out:Gender}`,
         #endif
         #trim-suffix ,
         FROM
           `%s#{str:TableUserInfoX(appID)}`
         WHERE
           `uid` = ?#{in:uid}
   ```

2. Generate DAO code

   ```bash
   godao < sample.yaml > sample.go
   ```

3. What you got (`sample.go`):

   ```go
   /*
    * Generated by Godao. DO NOT EDIT!
    */

   package main

   import (
        "bytes"
        "context"
        "database/sql"
        "errors"
        "fmt"
        "github.com/jmoiron/sqlx"
   )

   const (
        UserDAO_TableUserInfo = "user_info"
   )

   type UserDAO struct {
        db *sqlx.DB
   }

   func (self UserDAO) Tx(context_ context.Context, txOptions *sql.TxOptions, callback func(UserDAOTx) error) error {
        tx, e := self.db.BeginTxx(context_, txOptions)

        if e != nil {
                return e
        }

        txIsCommitted := false

        defer func() {
                if !txIsCommitted {
                        tx.Rollback()
                }
        }()

        if e := callback(UserDAOTx(tx)); e != nil {
                return e
        }

        if e := tx.Commit(); e != nil {
                return e
        }

        txIsCommitted = true
        return nil
   }

   type UserDAOTx *sqlx.Tx

   func MakeUserDAO(db *sqlx.DB) UserDAO {
        return UserDAO{db}
   }

   func (_self UserDAO) AddUserInfo(context_ context.Context, uid int64, nickname string, gender int8) (int64, error) {
        return _self.doAddUserInfo(_self.db, context_, uid, nickname, gender)
   }

   func (_self UserDAO) TxAddUserInfo(tx UserDAOTx, context_ context.Context, uid int64, nickname string, gender int8) (int64, error) {
        return _self.doAddUserInfo((*sqlx.Tx)(tx), context_, uid, nickname, gender)
   }

   func (UserDAO) doAddUserInfo(execer sqlx.ExecerContext, context_ context.Context, uid int64, nickname string, gender int8) (int64, error) {
        // INSERT INTO
        //   `%s#{str:TableUserInfo}` (`uid`, `nickname`, `gender`)
        // VALUES
        //   (?#{in:uid}, ?#{in:nickname}, ?#{in:gender})
        _buffer1 := [68]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [3]interface{}{}
        _args := _buffer3[:0]
        _raw_query = append(_raw_query, "INSERT INTO\n  `%s` (`uid`, `nickname`, `gender`)\nVALUES\n  (?, ?, ?)\n"...)
        _query_substrs = append(_query_substrs, UserDAO_TableUserInfo)
        _args = append(_args, uid, nickname, gender)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        _result, _e := execer.ExecContext(context_, _query, _args...)
        if _e != nil {
                return 0, _e
        }
        return _result.LastInsertId()
   }

   func (_self UserDAO) GetUserInfo(context_ context.Context, uid int64) (*UserInfo, error) {
        return _self.doGetUserInfo(_self.db, context_, uid)
   }

   func (_self UserDAO) TxGetUserInfo(tx UserDAOTx, context_ context.Context, uid int64) (*UserInfo, error) {
        return _self.doGetUserInfo((*sqlx.Tx)(tx), context_, uid)
   }

   func (UserDAO) doGetUserInfo(queryer sqlx.QueryerContext, context_ context.Context, uid int64) (*UserInfo, error) {
        // SELECT
        //   `uid#{out:UID}`, `nickname#{out:Nickname}`, `gender#{out:Gender}`
        // FROM
        //   `%s#{str:TableUserInfo}`
        // WHERE
        //   `uid` = ?#{in:uid}
        _buffer1 := [67]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [1]interface{}{}
        _args := _buffer3[:0]
        var _buffer4 UserInfo
        _record := &_buffer4
        _buffer5 := [3]interface{}{}
        _results := _buffer5[:0]
        _raw_query = append(_raw_query, "SELECT\n  `uid`, `nickname`, `gender`\nFROM\n  `%s`\nWHERE\n  `uid` = ?\n"...)
        _query_substrs = append(_query_substrs, UserDAO_TableUserInfo)
        _args = append(_args, uid)
        _results = append(_results, &_record.UID, &_record.Nickname, &_record.Gender)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        if _e := queryer.QueryRowxContext(context_, _query, _args...).Scan(_results...); _e != nil {
                if _e == sql.ErrNoRows {
                        _e = nil
                }
                return nil, _e
        }
        return _record, nil
   }

   func (_self UserDAO) SetUserInfo(context_ context.Context, uid int64, args *SetUserInfoArgs) (int64, error) {
        return _self.doSetUserInfo(_self.db, context_, uid, args)
   }

   func (_self UserDAO) TxSetUserInfo(tx UserDAOTx, context_ context.Context, uid int64, args *SetUserInfoArgs) (int64, error) {
        return _self.doSetUserInfo((*sqlx.Tx)(tx), context_, uid, args)
   }

   func (UserDAO) doSetUserInfo(execer sqlx.ExecerContext, context_ context.Context, uid int64, args *SetUserInfoArgs) (int64, error) {
        // UPDATE
        //   `%s#{str:TableUserInfo}`
        // SET
        // #if args.Nickname.Valid || args.Gender.Valid
        // #  if args.Nickname.Valid
        //   `nickname` = ?#{in:args.Nickname},
        // #  endif
        // #  if args.Gender.Valid
        //   `gender` = ?#{in:args.Gender},
        // #  endif
        // #  trim-suffix ,
        // #else
        // #  error errors.New("invalid args")
        // #endif
        // WHERE
        //   `uid` = ?#{in:uid}
        _buffer1 := [70]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [3]interface{}{}
        _args := _buffer3[:0]
        _raw_query = append(_raw_query, "UPDATE\n  `%s`\nSET\n"...)
        _query_substrs = append(_query_substrs, UserDAO_TableUserInfo)
        if args.Nickname.Valid || args.Gender.Valid {
                if args.Nickname.Valid {
                        _raw_query = append(_raw_query, "  `nickname` = ?,\n"...)
                        _args = append(_args, args.Nickname)
                }
                if args.Gender.Valid {
                        _raw_query = append(_raw_query, "  `gender` = ?,\n"...)
                        _args = append(_args, args.Gender)
                }
                _raw_query = trimSuffix_8d49903300a58635daf38603f2ecdebb16cdca2c(_raw_query, ",")
        } else {
                return 0, errors.New("invalid args")
        }
        _raw_query = append(_raw_query, "WHERE\n  `uid` = ?\n"...)
        _args = append(_args, uid)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        _result, _e := execer.ExecContext(context_, _query, _args...)
        if _e != nil {
                return 0, _e
        }
        return _result.RowsAffected()
   }

   func (_self UserDAO) AddMultiUserInfos(context_ context.Context, appID string, argsList []AddUserInfoArgs) (sql.Result, error) {
        return _self.doAddMultiUserInfos(_self.db, context_, appID, argsList)
   }

   func (_self UserDAO) TxAddMultiUserInfos(tx UserDAOTx, context_ context.Context, appID string, argsList []AddUserInfoArgs) (sql.Result, error) {
        return _self.doAddMultiUserInfos((*sqlx.Tx)(tx), context_, appID, argsList)
   }

   func (UserDAO) doAddMultiUserInfos(execer sqlx.ExecerContext, context_ context.Context, appID string, argsList []AddUserInfoArgs) (sql.Result, error) {
        // #if len(argsList) == 0
        // #  error errors.New("invalid argsList")
        // #endif
        // INSERT INTO
        //   `%s#{str:TableUserInfoX(appID)}` (`uid`, `nickname`, `gender`)
        // VALUES
        // #for i := range argsList
        // #  if i >= 1
        //   ,
        // #  endif
        //   (?#{in:argsList[i].UID}, ?#{in:argsList[i].Nickname}, ?#{in:argsList[i].Gender})
        // #endfor
        _buffer1 := [72]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [3]interface{}{}
        _args := _buffer3[:0]
        if len(argsList) == 0 {
                return nil, errors.New("invalid argsList")
        }
        _raw_query = append(_raw_query, "INSERT INTO\n  `%s` (`uid`, `nickname`, `gender`)\nVALUES\n"...)
        _query_substrs = append(_query_substrs, LocateUserInfoTable(context_, appID))
        for i := range argsList {
                if i >= 1 {
                        _raw_query = append(_raw_query, "  ,\n"...)
                }
                _raw_query = append(_raw_query, "  (?, ?, ?)\n"...)
                _args = append(_args, argsList[i].UID, argsList[i].Nickname, argsList[i].Gender)
        }
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        return execer.ExecContext(context_, _query, _args...)
   }

   func (_self UserDAO) GetMultiUserInfos(context_ context.Context, appID string, uids []int64) ([]*UserInfo, error) {
        return _self.doGetMultiUserInfos(_self.db, context_, appID, uids)
   }

   func (_self UserDAO) TxGetMultiUserInfos(tx UserDAOTx, context_ context.Context, appID string, uids []int64) ([]*UserInfo, error) {
        return _self.doGetMultiUserInfos((*sqlx.Tx)(tx), context_, appID, uids)
   }

   func (UserDAO) doGetMultiUserInfos(queryer sqlx.QueryerContext, context_ context.Context, appID string, uids []int64) ([]*UserInfo, error) {
        // SELECT
        //   `uid#{out:UID}`, `nickname#{out:Nickname}`, `gender#{out:Gender}`
        // FROM
        //   `%s#{str:TableUserInfoX(appID)}`
        // WHERE
        //   `uid` IN (?#{in:uids})
        _buffer1 := [70]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [1]interface{}{}
        _args := _buffer3[:0]
        _expand_args := false
        var _buffer4 UserInfo
        _record := &_buffer4
        _buffer5 := [3]interface{}{}
        _results := _buffer5[:0]
        _raw_query = append(_raw_query, "SELECT\n  `uid`, `nickname`, `gender`\nFROM\n  `%s`\nWHERE\n  `uid` IN (?)\n"...)
        _query_substrs = append(_query_substrs, LocateUserInfoTable(context_, appID))
        _args = append(_args, uids)
        _expand_args = true
        _results = append(_results, &_record.UID, &_record.Nickname, &_record.Gender)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        if _expand_args {
                var _e error
                _query, _args, _e = sqlx.In(_query, _args...)
                if _e != nil {
                        return nil, _e
                }
        }
        _rows, _e := queryer.QueryxContext(context_, _query, _args...)
        if _e != nil {
                return nil, _e
        }
        _records := []*UserInfo(nil)
        for _rows.Next() {
                if _e := _rows.Scan(_results...); _e != nil {
                        _rows.Close()
                        return nil, _e
                }
                _record_copy := new(UserInfo)
                *_record_copy = *_record
                _records = append(_records, _record_copy)
        }
        _rows.Close()
        return _records, nil
   }

   func (_self UserDAO) GetNicknameOfUserInfo(context_ context.Context, appID string, uid int64) (string, error) {
        return _self.doGetNicknameOfUserInfo(_self.db, context_, appID, uid)
   }

   func (_self UserDAO) TxGetNicknameOfUserInfo(tx UserDAOTx, context_ context.Context, appID string, uid int64) (string, error) {
        return _self.doGetNicknameOfUserInfo((*sqlx.Tx)(tx), context_, appID, uid)
   }

   func (UserDAO) doGetNicknameOfUserInfo(queryer sqlx.QueryerContext, context_ context.Context, appID string, uid int64) (string, error) {
        // SELECT
        //   `nickname#{out:nickname}`
        // FROM
        //   `%s#{str:TableUserInfoX(appID)}`
        // WHERE
        //   `uid` = ?#{in:uid}
        _buffer1 := [50]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [1]interface{}{}
        _args := _buffer3[:0]
        var _record string
        _buffer5 := [1]interface{}{}
        _results := _buffer5[:0]
        _raw_query = append(_raw_query, "SELECT\n  `nickname`\nFROM\n  `%s`\nWHERE\n  `uid` = ?\n"...)
        _query_substrs = append(_query_substrs, LocateUserInfoTable(context_, appID))
        _args = append(_args, uid)
        _results = append(_results, &_record)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        if _e := queryer.QueryRowxContext(context_, _query, _args...).Scan(_results...); _e != nil {
                return "", _e
        }
        return _record, nil
   }

   func (_self UserDAO) GetColumnsOfUserInfo(context_ context.Context, appID string, uid int64, args *UserInfoColumns) (*UserInfo, error) {
        return _self.doGetColumnsOfUserInfo(_self.db, context_, appID, uid, args)
   }

   func (_self UserDAO) TxGetColumnsOfUserInfo(tx UserDAOTx, context_ context.Context, appID string, uid int64, args *UserInfoColumns) (*UserInfo, error) {
        return _self.doGetColumnsOfUserInfo((*sqlx.Tx)(tx), context_, appID, uid, args)
   }

   func (UserDAO) doGetColumnsOfUserInfo(queryer sqlx.QueryerContext, context_ context.Context, appID string, uid int64, args *UserInfoColumns) (*UserInfo, error) {
        // #if !(args.GetNickname || args.GetGender)
        // #  error errors.New("invalid args")
        // #endif
        // SELECT
        // #if false
        //   `uid#{out:UID}`,
        // #endif
        // #if args.GetNickname
        //   `nickname#{out:Nickname}`,
        // #endif
        // #if args.GetGender
        //   `gender#{out:Gender}`,
        // #endif
        // #trim-suffix ,
        // FROM
        //   `%s#{str:TableUserInfoX(appID)}`
        // WHERE
        //   `uid` = ?#{in:uid}
        _buffer1 := [72]byte{}
        _raw_query := _buffer1[:0]
        _buffer2 := [1]interface{}{}
        _query_substrs := _buffer2[:0]
        _buffer3 := [1]interface{}{}
        _args := _buffer3[:0]
        var _buffer4 UserInfo
        _record := &_buffer4
        _buffer5 := [3]interface{}{}
        _results := _buffer5[:0]
        if !(args.GetNickname || args.GetGender) {
                return nil, errors.New("invalid args")
        }
        _raw_query = append(_raw_query, "SELECT\n"...)
        if false {
                _raw_query = append(_raw_query, "  `uid`,\n"...)
                _results = append(_results, &_record.UID)
        }
        if args.GetNickname {
                _raw_query = append(_raw_query, "  `nickname`,\n"...)
                _results = append(_results, &_record.Nickname)
        }
        if args.GetGender {
                _raw_query = append(_raw_query, "  `gender`,\n"...)
                _results = append(_results, &_record.Gender)
        }
        _raw_query = trimSuffix_8d49903300a58635daf38603f2ecdebb16cdca2c(_raw_query, ",")
        _raw_query = append(_raw_query, "FROM\n  `%s`\nWHERE\n  `uid` = ?\n"...)
        _query_substrs = append(_query_substrs, LocateUserInfoTable(context_, appID))
        _args = append(_args, uid)
        _query := fmt.Sprintf(string(_raw_query), _query_substrs...)
        if _e := queryer.QueryRowxContext(context_, _query, _args...).Scan(_results...); _e != nil {
                if _e == sql.ErrNoRows {
                        _e = nil
                }
                return nil, _e
        }
        return _record, nil
   }

   type UserInfo struct {
        UID      int64
        Nickname string
        Gender   int8
   }

   type SetUserInfoArgs struct {
        Nickname sql.NullString
        Gender   sql.NullInt64
   }

   type AddUserInfoArgs struct {
        UID      int64
        Nickname string
        Gender   int8
   }

   type UserInfoColumns struct {
        GetNickname bool
        GetGender   bool
   }

   func trimSuffix_8d49903300a58635daf38603f2ecdebb16cdca2c(rawQuery []byte, suffix string) []byte {
        n := len(rawQuery)
        i := n

   Loop:
        for i >= 1 {
                switch rawQuery[i-1] {
                case '\t', '\n', '\v', '\f', '\r', ' ':
                default:
                        break Loop
                }

                i--
        }

        if i >= 1 && bytes.HasSuffix(rawQuery[:i], []byte(suffix)) {
                j := i - len(suffix)

                for i < n {
                        rawQuery[j] = rawQuery[i]
                        i++
                        j++
                }

                rawQuery = rawQuery[:j]
        }

        return rawQuery
   }
   ```
