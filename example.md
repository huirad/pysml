# One block of data sent by the ED300L

Note: privacy relevant data are replaced with XX or YY

```
1b 1b 1b 1b 01 01 01 01 76 07 00 08 17 31 4b 30
62 00 62 00 72 63 01 01 76 01 01 07 00 08 0c 6a
19 10 0b 06 45 4d 48 XX XX XX XX XX XX 01 01 63
b8 a0 00 76 07 00 08 17 31 4b 31 62 00 62 00 72
63 07 01 77 01 0b 06 45 4d 48 XX XX XX XX XX XX
01 72 62 01 65 0c 6a 50 b5 77 77 07 81 81 c7 82
03 ff 01 01 01 01 04 45 4d 48 01 77 07 01 00 00
00 09 ff 01 01 01 01 0b 06 45 4d 48 01 02 71 59
09 6d 01 77 07 01 00 01 08 00 ff 63 01 82 01 62
1e 52 ff 56 00 04 eb 09 6c 01 77 07 01 00 01 08
01 ff 01 01 62 1e 52 ff 56 00 04 eb 09 6c 01 77
07 01 00 01 08 02 ff 01 01 62 1e 52 ff 56 00 00
00 00 00 01 77 07 01 00 0f 07 00 ff 01 01 62 1b
52 ff 55 00 00 0a f0 01 77 07 81 81 c7 82 05 ff
01 01 01 01 83 02 95 a0 df c1 YY YY YY YY YY YY
YY YY YY YY YY YY YY YY YY YY YY YY YY YY YY YY
YY YY YY YY YY YY YY YY YY YY YY YY YY YY YY YY
YY YY cb 9d 29 52 01 01 01 63 7c 03 00 76 07 00
08 17 31 4b 34 62 00 62 00 72 63 02 01 71 01 63
71 14 00 00 1b 1b 1b 1b 1a 01 b9 20
```

# Important data types

```
SML_Message ::= SEQUENCE
{
  transactionId Octet String,
  groupNo Unsigned8,
  abortOnError Unsigned8,
  messageBody SML_MessageBody,
  crc16 Unsigned16,
  endOfSmlMsg EndOfSmlMsg -- always 00
}
```

```
SML_PublicOpen.Res ::= SEQUENCE
{
  codepage Octet String OPTIONAL,
  clientId Octet String OPTIONAL,
  reqFileId Octet String,
  serverId Octet String,
  refTime SML_Time OPTIONAL,
  smlVersion Unsigned8 OPTIONAL,
}
```

```
SML_GetList.Res ::= SEQUENCE
{
  clientId Octet String OPTIONAL,
  serverId Octet String,
  listName Octet String OPTIONAL,
  actSensorTime SML_Time OPTIONAL,
  valList SML_List,
  listSignature SML_Signature OPTIONAL,
  actGatewayTime SML_Time OPTIONAL
}
```

```
SML_List ::= SEQUENCE OF
{
  valListEntry SML_ListEntry
}
```

```
SML_ListEntry ::= SEQUENCE
{
  objName Octet String,
  status SML_Status OPTIONAL,
  valTime SML_Time OPTIONAL,
  unit SML_Unit OPTIONAL,
  scaler Integer8 OPTIONAL,
  value SML_Value,
  valueSignature SML_Signature OPTIONAL
}
```


```
SML_PublicClose.Res ::= SEQUENCE
{
  globalSignature SML_Signature OPTIONAL
}
```

# Now the decoded, annotated Block


```

-- Start sequence
1b 1b 1b 1b                                     -- Escape sequence
01 01 01 01                                     -- SML version 1      


-- 1st SML_Message
76                                              -- SML_Message is a list (7) with 6 elements
   07 00 08 17 31 4b 30                         -- transactionId Octet String
   62 00                                        -- groupNo Unsigned8
   62 00                                        -- abortOnError Unsigned8
   
   72                                           -- messageBody SML_MessageBody is a list with 2 elements
      63 01 01                                  -- TAG: OpenResponse
      76                                        -- SML_PublicOpen.Res is a list of 6 elements
         01                                     -- codepage Octet String OPTIONAL
         01                                     -- clientId Octet String OPTIONAL
         07 00 08 0c 6a 19 10                   -- reqFileId Octet String
         0b 06 45 4d 48 XX XX XX XX XX XX       -- serverId Octet String (same as printed on the device; 45 4d 48 = EMH)
         01                                     -- refTime SML_Time OPTIONAL
         01                                     -- smlVersion Unsigned8 OPTIONAL
   63 b8 a0                                     -- crc16 Unsigned16
   00                                           -- endOfSmlMsg EndOfSmlMsg

-- 2nd SML_Message
76                                              -- SML_Message is a list (7) with 6 elements
   07 00 08 17 31 4b 31                         -- transactionId Octet String
   62 00                                        -- groupNo Unsigned8
   62 00                                        -- abortOnError Unsigned8
   
   72                                           -- messageBody SML_MessageBody is a list with 2 elements
      63 07 01                                  -- TAG: GetListResponse
      77                                        -- SML_GetList.Res is a list of 7 elements

         01                                     -- clientId Octet String OPTIONAL
         0b 06 45 4d 48 01 02 71 59 09 6d       -- serverId Octet String
         01                                     -- listName Octet String OPTIONAL
         72                                     -- actSensorTime SML_Time OPTIONAL
            62 01                               -- TAG: secIndex
            65 0c 6a 50 b5                      -- secIndex Unsigned32
         77                                     -- valList SML_List

            77                                  -- SML_ListEntry is a list of 7 elements
               07 81 81 c7 82 03 ff             -- objName Octet String | Herstellerkennung
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               01                               -- unit SML_Unit OPTIONAL
               01                               -- scaler Integer8 OPTIONAL
               04 45 4d 48                      -- value SML_Value | octet string "EMH"
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 01 00 00 00 09 ff             -- objName Octet String | OBIS oid for Geraete-Identifikation 
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               01                               -- unit SML_Unit OPTIONAL
               01                               -- scaler Integer8 OPTIONAL
               0b 06 45 4d 48 XX XX XX XX XX XX -- value SML_Value | serverId Octet String (same as printed on the device; 45 4d 48 = EMH)
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 01 00 01 08 00 ff             -- objName Octet String | OBIS oid for Zählwerk positive Wirkenergie, tariflos
               63 01 82                         -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               62 1e                            -- unit SML_Unit OPTIONAL | 1e = 30 -> Wh (see https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf, table 4 / page 47)
               52 ff                            -- scaler Integer8 OPTIONAL | ff = -1 -> unit + scaler results in 10^-1 Wh
               56 00 04 eb 09 6c                -- value SML_Value | Unsigned40: 82512236 | translates to ca 8251 kWh 
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 01 00 01 08 01 ff             -- objName Octet String | OBIS oid for Zählwerk positive Wirkenergie, Tarif 1
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               62 1e                            -- unit SML_Unit OPTIONAL | 1e = 30 -> Wh (see https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf, table 4 / page 47)
               52 ff                            -- scaler Integer8 OPTIONAL | ff = -1 -> unit + scaler results in 10^-1 Wh
               56 00 04 eb 09 6c                -- value SML_Value | Unsigned40: 82512236 | translates to ca 8251 kWh 
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 01 00 01 08 02 ff             -- objName Octet String | OBIS oid for Zählwerk positive Wirkenergie, Tarif 2
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               62 1e                            -- unit SML_Unit OPTIONAL | 1e = 30 -> Wh (see https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf, table 4 / page 47)
               52 ff                            -- scaler Integer8 OPTIONAL | ff = -1 -> unit + scaler results in 10^-1 Wh
               56 00 00 00 00 00                -- value SML_Value | Unsigned40: 0
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 01 00 0f 07 00 ff             -- objName Octet String | OBIS oid for Aktuelle pos. Wirkleistung Betrag
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               62 1b                            -- unit SML_Unit OPTIONAL | 1b = 27 -> W (see https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf, table 4 / page 47)
               52 ff                            -- scaler Integer8 OPTIONAL | ff = -1 -> unit + scaler results in 10^-1 W
               55 00 00 0a f0                   -- value SML_Value | Unsigned32: 2800 | translates to 280W
               01                               -- valueSignature SML_Signature OPTIONAL

            77                                  -- SML_ListEntry is a list of 7 elements
               07 81 81 c7 82 05 ff             -- objName Octet String | OBIS oid for Public Key
               01                               -- status SML_Status OPTIONAL
               01                               -- valTime SML_Time OPTIONAL
               01                               -- unit SML_Unit OPTIONAL
               01                               -- scaler Integer8 OPTIONAL
               83 02                            -- 50 Byte octet string - the first 48 bytes are same as public key printed on device
                 95 a0 df c1 YY YY YY YY        -- 08
                 YY YY YY YY YY YY YY YY        -- 16
                 YY YY YY YY YY YY YY YY        -- 24
                 YY YY YY YY YY YY YY YY        -- 32
                 YY YY YY YY YY YY YY YY        -- 40
                 YY YY YY YY cb 9d 29 52        -- 48
                 01 01                          -- 50
               01                               -- valueSignature SML_Signature OPTIONAL

         63 7c 03                               -- crc16 Unsigned16
         00                                     -- endOfSmlMsg EndOfSmlMsg

-- 3rd SML_Message
76                                              -- SML_Message is a list (7) with 6 elements 
   07 00 08 17 31 4b 34                         -- transactionId Octet String
   62 00                                        -- groupNo Unsigned8
   62 00                                        -- abortOnError Unsigned8
   
   72                                           -- messageBody SML_MessageBody is a list with 2 elements     
     63 02 01                                   -- TAG: CloseResponse
     71                                         -- SML_PublicClose.Res is a list with 1 element
        01                                      -- globalSignature SML_Signature OPTIONAL
   63 71 14                                     -- crc16 Unsigned16
   00                                           -- endOfSmlMsg EndOfSmlMsg
00                                              -- padding byte 


-- End sequence
1b 1b 1b 1b                                     -- Escape sequence
1a 01 b9 20                                     -- 1a xx yy zz  | 1a of message | xx = 01: number of padding bytes | yy zz = crc16 
```