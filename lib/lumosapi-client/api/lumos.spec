# This spec uses OData v4.0 as a guideline
# http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html
openapi: 3.0.0
info:
  contact:
    name: "Spectra Logic Corporation"
    url: "https://support.spectralogic.com/"
  title: Spectra Logic - LumOS Tape Library Management
  version: 1.0.0
  description: |-
    Configure and Manage Library Resources
    LumOS and the LumOS Tape Library REST API © Spectra Logic Corp

    Deprecation Policy:
      Deprecated endpoints, methods or fields will be supported in any LumOS packages released in the 6 months following the first release containing the deprecation.
      Services that have been deprecated may be supported longer than 6 months on a case by case basis.
      Deprecations and removals will be listed in the patch notes for that release and current deprecated endpoints, methods and fields will also be marked in the API spec.
      Endpoints marked with the "x-experimental" property are not subject to the above policy and may be changed or removed at any time.
servers:
  - url: https://{server}:{port}/api
    variables:
      server:
        default: localhost
        description: Secure URI to a Managed Spectra Logic library
      port:
        default: '443'
tags:
  - name: Cube
    description: Supported on Cube libraries.
  - name: TFinity
    description: Supported on TFinity libraries.
  - name: Python
    description: Supported on Python libraries.
paths:
  /spec:
    get:
      summary: Retrieve this Document
      description: |-
        Retrieves the current OpenAPI spec document.
        The Accept header can be used to control response type.

        * application/json - return this specification in JSON format

        * application/x-yaml - return this specification in YAML format
      operationId: GetAPIDocumentation
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                format: json
            application/x-yaml:
              schema:
                format: yaml
        default:
          $ref: '#/components/responses/default'
  /backups:
    get:
      summary: Retrieve a List of Stored Backups
      description: Returns a paginated list of both manually and automatically generated backups currently stored on the library in order of newest to oldest.
      operationId: GetBackups
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BackupList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Create A Backup
      description: Creates a manual backup. Manual backups must be manually deleted once the 30 manual backup limit is reached, in order to create another manual backup.
      operationId: CreateBackup
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BackupRequest'
        required: true
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Backup'
        default:
          $ref: '#/components/responses/default'
  /backups/upload:
    post:
      summary: Upload a Backup
      description: |-
        Uploads a saved backup file to the library. After the upload, the backup file is re-categorized as a manual backup.
        The backup file name must be of the format `<librarySerialNumber>_<date>T<time>.tar.gz`, where `<date>` is in the format
        `YYYY-MM-DD` and `<time>` is in the format `HHMMSSZ`. The Z in the timestamp specifies that the timezone used is UTC.
        Example: `0123456789_2023-12-31T123000Z.tar.gz`
      operationId: UploadBackup
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      parameters:
        - description: Automatically apply backup after uploading
          name: apply
          in: query
          schema:
            type: boolean
            default: false
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Backup'
        default:
          $ref: '#/components/responses/default'
  '/backups/{name}':
    parameters:
      - $ref: '#/components/parameters/backupName'
    get:
      summary: Get Metadata for a Stored Backup
      description: Retrieves the metadata for the specified backup.
      operationId: GetBackupInfo
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Backup'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a Stored Backup
      description: Deletes a backup stored on the library
      operationId: DeleteBackup
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Restore Library from a Backup
      description: Restores the library configuration using the specified backup.
      operationId: RestoreToBackup
      x-permitted-roles: [ SuperUser ]
      tags: [ Cube, TFinity, Python ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  '/backups/{name}/download':
    parameters:
      - $ref: '#/components/parameters/backupName'
    get:
      summary: Download a Backup
      description: Download the specified backup file on the library.
      operationId: DownloadBackup
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/x-gzip:
              schema:
                type: string
                format: binary
        default:
          $ref: '#/components/responses/default'
  /chambers:
    get:
      summary: Retrieve library chamber information.
      description: Retrieve information about library chamber availability, grouped by media type. Note - each chamber is counted once for every media type it supports; therefore the sum of all available chambers in this response will generally be larger than the number of actual empty chambers in the library.
      operationId: GetChambers
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ChamberInfo'
        default:
          $ref: '#/components/responses/default'
  /dlm-records:
    get:
      summary: Retrieve DLM Data
      description: Retrieve a Drive Lifecycle Management (DLM) report filtered by the provided query parameters.
      operationId: GetDLM
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DLMList'
              examples:
                dlmList:
                  $ref: '#/components/examples/dlmList'
        default:
          $ref: '#/components/responses/default'
  /dlm-records/{ManufacturerSerialNumber}:
    parameters:
      - description: The manufacturer serial number of the drive. This is returned as `manufacturerSerialNumber` in the response from `GET /frus`.
        required: true
        name: ManufacturerSerialNumber
        in: path
        schema:
          type: string
          minLength: 10
          maxLength: 16
        example: "10WT000234"
    get:
      summary: Retrieve DLM Data by Serial Number
      description: Retrieve a DLM report for the drive specified by serial number.
      operationId: GetDLMRecord
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DLMRecord'
              examples:
                dlmData:
                  $ref: '#/components/examples/dlmData'
        default:
          $ref: '#/components/responses/default'
  /dlm-records/{ManufacturerSerialNumber}/history:
    parameters:
      - description: The manufacturer serial number of the drive. This is returned as `manufacturerSerialNumber` in the response from `GET /frus`.
        required: true
        name: ManufacturerSerialNumber
        in: path
        schema:
          type: string
        example: "10WT000234"
      - $ref: '#/components/parameters/offsetParam'
      - $ref: '#/components/parameters/limitParam'
    get:
      summary: Retrieve DLM load history by Serial Number
      description: Retrieve DLM load history for the drive specified by serial number.
      operationId: GetDLMLoadHistory
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoadHealthHistory'
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/keys:
    get:
      summary: Get BlueScale encryption key information.
      description: |-
        Return a list of the currently installed BlueScale encryption key information.
      operationId: GetBlueScaleEncryptionKeys
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser, Admin ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BlueScaleEncryptionKeyInfo'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Create a BlueScale encryption key.
      description: Create a BlueScale encryption key with the provided moniker. Spectra Logic recommends exporting the key immediately after creation.
      operationId: CreateBlueScaleEncryptionKey
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                moniker:
                  $ref: '#/components/schemas/BlueScaleEncryptionMoniker'
                authorization:
                  description: Password used to authorize this operation. Use Encryption-Authorization header for this field.
                  $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  deprecated: true
              required:
                - moniker
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                type: object
                properties:
                  keyInfo:
                    $ref: '#/components/schemas/BlueScaleEncryptionKeyInfo'
                required:
                  - keyInfo
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/keys/export:
    post:
      summary: Export a key.
      description:
        Export a BlueScale encryption key identified by the provided moniker. The provided password is used to encrypt the key and must be provided when importing the associated key.
      operationId: ExportBlueScaleEncryptionKey
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
        - name: Secondary-Encryption-Authorization
          in: header
          description: Additional password used to authorize this operation in multi user mode.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                moniker:
                  $ref: "#/components/schemas/BlueScaleEncryptionMoniker"
                password:
                  description: Password used to encrypt the key.
                  $ref: '#/components/schemas/BlueScaleEncryptionKeyPassword'
                authorization:
                  type: array
                  minItems: 1
                  items:
                    $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  description: Passwords used to authorize this operation. Only one password is required in single user mode. Two passwords are required for mutli user mode. Use Encryption-Authorization and Secondary-Encryption-Authorization header for this field.
                  deprecated: true
              required:
                - moniker
                - password
      responses:
        '200':
          description: OK
          content:
            text/plain:
              schema:
                description: The encrypted key file as [moniker].bsk
                type: string
                format: binary
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/keys/import:
    post:
      summary: Import a key.
      description:
        Import a BlueScale encryption key. The provided password is used to decrypt the key and must match the password entered when the key was exported.
      operationId: ImportBlueScaleEncryptionKey
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
        - name: Secondary-Encryption-Authorization
          in: header
          description: Additional password used to authorize this operation in multi user mode.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                keyFile:
                  description: The encrypted key file as [moniker].bsk
                  type: string
                  format: binary
                password:
                  $ref: '#/components/schemas/BlueScaleEncryptionKeyPassword'
                authorization:
                  type: array
                  items:
                    $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  description: Passwords used to authorize this operation. Only one password is required in single user mode. Two passwords are required for multi user mode. Use Encryption-Authorization and Secondary-Encryption-Authorization header for this field.
                  deprecated: true
              required:
                - keyFile
                - password
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BlueScaleEncryptionKeyInfo'
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/keys/monikers/{moniker}:
    parameters:
      - description: Key moniker.
        name: moniker
        in: path
        schema:
          $ref: '#/components/schemas/BlueScaleEncryptionMoniker'
        required: true
    delete:
      summary: Delete a BlueScale encryption key.
      description: Delete a BlueScale encryption key identified by the provided moniker. Caution - this may result in data loss unless the encryption key was previously exported.
      operationId: DeleteBlueScaleEncryptionKey
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          description: Passwords used to authorize this operation.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                authorization:
                  description: Use Encryption-Authorization header for this field.
                  $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  deprecated: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/secure-initialization/authorize:
    put:
      summary: Authorize completion of the BlueScale encryption secure initialization process.
      description: Provide an authorization password to complete the BlueScale encryption secure initialization process.
      operationId: AuthorizeBlueScaleEncryptionSecureInitialization
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          description: Passwords used to authorize this operation.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                authorization:
                  description: Use Encryption-Authorization header for this field.
                  $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  deprecated: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /encryption/bluescale/secure-initialization/state:
    get:
      summary: Get the current BlueScale encryption secure initialization state.
      description: |-
        Returns the current state of the BlueScale encryption secure initialization process.
        When secure initialization is enabled, completion of the process must be authorized at
        /encryption/bluescale/secure-initialization/authorize after each library power up.
      operationId: GetBlueScaleEncryptionSecureInitializationState
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  state:
                    $ref: '#/components/schemas/BlueScaleEncryptionSecureInitializationState'
                required:
                  - state
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/certificates/signing-request:
    post:
      summary: Generate a certificate signing request.
      description: |-
        Generate a PKCS#10 formatted certificate signing request with the provided information that can be used to
        generate a certificate for the library.
      operationId: CreateKMIPCertificateSigningRequest
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                distinguishedName:
                  $ref: '#/components/schemas/X509DistinguishedName'
              required:
                - distinguishedName
        required: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  csr:
                    type: string
                    description: PEM encoded certificate signing request.
                required:
                  - csr
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/certificates:
    post:
      summary: Import certificates for KMIP servers.
      description: |-
        Import a client certificate for the library to provide when communicating with a KMIP server as well as the local
        certificate authority (CA) certificate for the library to use when verifying the KMIP server's certificate.
        The client certificate should be generated using the library's certificate signing request and the local CA
        certificate.
      operationId: ImportKMIPCertificates
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                libraryCertificate:
                  description: PEM encoded client certificate for the library created using the library's certificate
                    signing request and local CA certificate.
                  type: string
                localCACertificate:
                  description: PEM encoded local certificate authority (CA) certificate for the library to use when
                    verifying the KMIP server's certificate.
                  type: string
              required:
                - libraryCertificate
                - localCACertificate
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/distinguished-name/active:
    get:
      summary: Retrieve the active distinguished name.
      description: Retrieve the active distinguished name that was configured with the most recently uploaded certificates.
      operationId: GetActiveKMIPDistinguishedName
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/X509DistinguishedName'
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/distinguished-name/pending:
    get:
      summary: Retrieve the pending distinguished name.
      description: Retrieve the pending distinguished name that was used to generate the most recent certificate signing request.
      operationId: GetPendingKMIPDistinguishedName
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/X509DistinguishedName'
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/servers:
    get:
      summary: Get KMIP server information.
      description: |-
        Return a list of the currently configured KMIP servers.
      operationId: GetKMIPServers
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/KMIPServer'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add KMIP server
      description: |-
        Add a new KMIP server configuration for the library.
        The library will use the installed client certificate and local CA certificate to communicate with the server.
        A total of 4 KMIP servers can be configured.
      operationId: AddKMIPServer
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                address:
                  type: string
                  description: The IP address or hostname of the KMIP server.
                port:
                  type: integer
                  description: The port number of the KMIP server.
                  minimum: 1
                  maximum: 65535
              required:
                - address
                - port
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/KMIPServer'
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/servers/{serverID}:
    parameters:
      - description: The ID of the KMIP server.
        name: serverID
        in: path
        required: true
        schema:
          type: string
    delete:
      summary: Delete KMIP server
      description: |-
        Delete a KMIP server configuration from the library.
      operationId: DeleteKMIPServer
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Update KMIP server
      description: |-
        Update the configuration of a KMIP server.
      operationId: UpdateKMIPServer
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                address:
                  type: string
                  description: The IP address or hostname of the KMIP server.
                port:
                  type: integer
                  description: The port number of the KMIP server.
                  minimum: 1
                  maximum: 65535
              required:
                - address
                - port
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/KMIPServer'
        default:
          $ref: '#/components/responses/default'
  /encryption/kmip/servers/{serverID}/status:
    parameters:
      - description: The ID of the KMIP server.
        name: serverID
        in: path
        required: true
        schema:
          type: string
    get:
      summary: Get KMIP server status.
      description: |-
        Return the status of a KMIP server.
      operationId: GetKMIPServerStatus
      tags: [ TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          required: true
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/KMIPServerStatus'
        default:
          $ref: '#/components/responses/default'
  /events/topics:
    get:
      summary: Get Event Topics
      description: |-
        Get the list of topics which can be used in requests to `GET /events/sse`.
      operationId: GetEventTopics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/EventTopic'
        default:
          $ref: '#/components/responses/default'
  /events/sse:
    get:
      summary: Receive SSE Events Stream
      description: Begin receiving events through SSE as they occur. A `Topics` event, whose payload is a list of the available `EventTopic`s, is sent when a new client first connects.
      operationId: GetEventsSSE
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - description: Topic name filter to be applied, in a comma separated list.  This is returned as `name` in `GET /events`.
          name: 'topics'
          in: query
          schema:
            type: array
            items:
              type: string
          explode: false
          examples:
            Drive Added:
              description: Get events associated with drives added in Key:Value pair format
              value: [ "Drive Added" ]
            Drive Removed:
              description: Get events associated with drives removed in Key:Value pair format
              value: [ "Drive Removed" ]
      responses:
        '200':
          description: OK
          content:
            text/event-stream:
              schema:
                description: |-
                  Information about server initiated events as a stream of packets.
                  Response will always set header Transfer-Encoding: chunked.
                  Events are formatted as key:value pairs with a blank line between events.
                type: array
                items:
                  $ref: '#/components/schemas/Event'
        default:
          $ref: '#/components/responses/default'
  /firmware/drives/stage:
    get:
      summary: Get drive firmware staging information
      description:
        Get the staging status for all drives assigned to a partition.
      operationId: GetDriveFirmwareStaging
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DriveFirmwareStagingInfo'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Stage drive firmware
      description: |-
        - Stage the provided drive firmware file to the specified drives. The firmware file must be a signed drive
        - firmware file from Spectra Logic. Additionally, the firmware file must be compatible with the generation,
        - height, and connection type of the drive. Only one firmware staging operation can be active at a time.
        - This is a long running operation that can take up to 12 hours to complete.
      operationId: StartStageDriveFirmware
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: List of drives to stage.
          name: drives
          in: query
          required: true
          explode: false
          style: form
          schema:
            type: array
            items:
              type: string
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                firmwareFile:
                  description: |-
                    - The drive firmware file to stage the drive with.
                    - The name must have the format <vendor>-<type>-<profile>-<port_type>-<version>-<date>.d[l|t]s.
                    - example: IBM-LTO6-FH-Fibre_KAJ8-20220308D.dls
                  type: string
                  format: binary
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /firmware/drives/stage/abort:
    put:
      summary: Abort the current drive firmware staging operation
      description: Stop the drive firmware staging operation that is currently in progress.
      operationId: AbortDriveFirmwareStaging
      tags: [ TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /firmware/drives/commit:
    get:
      summary: Get drive firmware commit information
      description:
        Get the commit status of all present drives within the library.
      operationId: GetDriveCommitInfo
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DriveFirmwareCommitInfo'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Commit drive firmware
      description: |-
        - Commit the staged drive firmware to the specified drives. This operation will take about 10 minutes and
        - will power cycle the specified drives. Note: The staged firmware will be cleared regardless of whether or not
        - the commit operation succeeds.
      operationId: StartCommitDriveFirmware
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: List of drives to commit.
          name: drives
          in: query
          required: true
          explode: false
          style: form
          schema:
            type: array
            items:
              type: string
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /frame-count:
    get:
      summary: Retrieve library frame count.
      description: Retrieve the number of frames in the library.
      operationId: GetFrameCount
      tags: [ Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
              application/json:
                schema:
                  type: object
                  required:
                    - frameCount
                  properties:
                    frameCount:
                      type: integer
                      description: The number of frames in the library.
        default:
          $ref: '#/components/responses/default'
  /frus:
    get:
      summary: Get Metadata for FRUs in the library
      description: Retrieve a list of hardware field replaceable units currently in the library.
      operationId: GetFRUs
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - description: Type of field replaceable unit to return. If not included, information for all types of FRUs is returned.
          name: 'types'
          in: query
          explode: false
          required: false
          schema:
            type: array
            items:
              $ref: '#/components/schemas/FRUTypes'
          examples:
            single:
              value:
                - "DRIVE"
            multiple:
              value:
                - "DRIVE"
                - "ROBOT"
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FRUList'
        default:
          $ref: '#/components/responses/default'
  '/frus/{name}':
    parameters:
      - $ref: '#/components/parameters/fruName'
    get:
      summary: Get Metadata for a Single FRU
      description: Get metadata for the specified FRU by name.
      operationId: GetFRU
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FRU'
        default:
          $ref: '#/components/responses/default'
  '/frus/{name}/actions/{action}':
    parameters:
      - $ref: '#/components/parameters/fruName'
      - description: Action to perform.  One of the list of `actions` for a given FRU returned from `GET /frus` or `Get /frus/{name}`.
        name: action
        in: path
        required: true
        schema:
          $ref: '#/components/schemas/FRUActions'
    post:
      summary: Send Action to a FRU
      description: Send control actions to the specified FRU.
      operationId: StartFRUAction
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/frus/{name}/status':
    parameters:
      - $ref: '#/components/parameters/fruName'
    get:
      summary: Retrieve Status of a Field Replaceable Unit
      description: Retrieve the Status of a specified field replaceable unit
      operationId: GetFRUStatus
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FRUStatus'
        default:
          $ref: '#/components/responses/default'
  /inventory:
    get:
      summary: Retrieve a List of Inventory from the Library
      description: Retrieve a list of inventory currently in the library.
      operationId: GetInventory
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/containerType'
        - $ref: '#/components/parameters/mediaType'
        - description: The barcode of a tape cartridge. If included, only information about the matching tape cartridges is returned. If not included, information about all tape cartridges is returned.
          name: mediaBarcode
          in: query
          schema:
            type: string
          examples:
            LTO8:
              value: ASD124L8
            Cleaning:
              value: CLN00001
          required: false
        - name: state
          in: query
          description: Returns media filtered by accessible or inaccessible. By default, media are not filtered by accessibility.
          schema:
            $ref: '#/components/schemas/ElementStateType'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaContainerList'
        default:
          $ref: '#/components/responses/default'
  '/inventory/actions/{action}':
    parameters:
      - description: Action to perform.
        name: action
        in: path
        required: true
        schema:
          $ref: '#/components/schemas/InventoryActions'
    post:
      summary: Execute an action on the inventory
      description: Execute an action on the inventory
      operationId: StartInventoryAction
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /inventory/actions/resolve-slot-iq:
    post:
      summary: Resolve SlotIQ
      description: Physically complete all outstanding virtual drive to slot moves across all partitions.
      operationId: ResolveSlotIQ
      tags: [ Cube, TFinity ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /inventory/actions/unload-drives:
    post:
      parameters:
        - in: query
          name: partitionName
          schema:
            type: string
          description: The name of the partition whose drives will be unloaded. If not provided, all drives across all partitions will be unloaded.
      summary: Unload Drives
      description: Unload all drives in the library or a specific partition. Tapes are unloaded into the first available slots in the Storage pool of the specified partition.
      operationId: UnloadDrives
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          description: Returns a task ID for each full drive to be unloaded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskIdList'
        default:
          $ref: '#/components/responses/default'
  /library:
    get:
      summary: Retrieve Basic Library Information
      description: Retrieve metadata about the library.
      operationId: GetLibraryInfo
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BasicInfo'
        default:
          $ref: '#/components/responses/default'
  /library/actions/{action}:
    post:
      summary: Start an Action Affecting the Entire Library
      description: Start an action which will affect the entire library.
      operationId: StartLibraryAction
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: Action to perform
          name: action
          required: true
          in: path
          schema:
            $ref: '#/components/schemas/LibraryActions'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics:
    get:
      summary: Retrieve Library Diagnostics
      description: Retrieves list of all pending, running or completed library diagnostics. All users can access this
        endpoint, but only diagnostics that the user has permission to view are returned.
      operationId: GetLibraryDiagnostics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - description: The type of diagnostic to return. If not provided, all diagnostic types are included.
          name: type
          in: query
          schema:
            $ref: '#/components/schemas/LibraryDiagnosticType'
          required: false
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryDiagnosticList'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/delete-geometry:
    post:
      summary: Delete robotic geometry.
      description: -|
        This diagnostic deletes the existing robotic geometry and then rediscovers the physical layout and geometry of
        the library. The inventory of the library is preserved during this operation. NOTE - Remove all tapes from tape
        drives before running this diagnostic, since all loaded tapes will be inaccessible after running this diagnostic.
        This diagnostic can be helpful to run after making physical alterations to the library such as replacing
        robotic columns, replacing transporters or changing alignments.
      operationId: StartDeleteGeometryDiagnostic
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/move-tape-to-drives:
    post:
      summary: Move the specified tape to all the drives in the tape's partition.
      description: -|
        This diagnostic moves the specified tape to all drives in the tape's partition.
        This diagnostic typically takes up to two minutes per drive to complete.
        If robotics geometry has been reset recently, it can take up to five minutes per drive.
        Warning- Any host moves that are received while this diagnostic is running will fail.  Drives must be unloaded before running this diagnostic.
      operationId: StartMoveTapeToDrivesDiagnostic
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveTapeToDrivesTest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/move-to-all-chambers:
    post:
      summary: Start a Move To All Chambers diagnostic
      description: |-
        This diagnostic moves a TeraPack magazine to each chamber in the library to verify the physical integrity of the
        library and to identify any blockages. The diagnostic takes up to one hour per frame to complete. Moves will be
        failed during the diagnostic. This diagnostic behavior can be achieved on other library types by running a
        move-to-chambers diagnostic and providing an asterisk for each value in the location field (*:*:*:*).
      operationId: StartMoveToAllChambersDiagnostic
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/obstruction-scan:
    post:
      summary: Start an Obstruction Scan diagnostic
      description: |-
        This diagnostic scans for potential obstructions to robotic movement. The scan takes approximately two minutes
        per frame. Host moves are delayed during the scan.
      operationId: StartObstructionScanDiagnostic
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/move-to-chambers:
    post:
      summary: Start a Move To Chambers diagnostic
      description: |-
        This test moves magazines to and from the specified chamber(s). Running this validates fault-free access to a magazine
        in each chamber tested. Providing no parameters will run the test against all chambers.
      operationId: StartMoveToChambersDiagnostic
      tags: [ Cube, TFinity ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: false
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveToChambersTest'
            examples:
              SingleChamber:
                summary: The 2nd chamber in the 6th bay of the first frame on the left side of a Cube library
                value:
                  robotName: "Robot:1"
                  splitCoverage: false
                  location: "1:L:6:2"
              AllChambersInOneBay:
                summary: All chambers in the first bay of the first frame on the right side of a Cube library
                value:
                  robotName: "Robot:1"
                  splitCoverage: false
                  location: "1:R:1:*"
              AllChambersInAllBaysOnOneSide:
                summary: All chambers in all bays of the first frame on the left side of a Cube library
                value:
                  robotName: "Robot:1"
                  splitCoverage: false
                  location: "1:L:*:*"
              AllChambersInAllBaysOnBothSides:
                summary: All chambers in all bays on both sides of the first and only frame of a Cube library
                value:
                  robotName: "Robot:1"
                  splitCoverage: false
                  location: "1:*:*:*"
              AllChambersOnInEveryFrameOnOneSide:
                summary: All chambers on the right side of a Cube library
                value:
                  robotName: "Robot:1"
                  splitCoverage: false
                  location: "*:R:*:*"
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/move-to-shelf:
    post:
      summary: Start a Move To Shelf diagnostic
      description: |-
        This test will move the first available TeraPack magazine to all chambers of the specified shelf. Moves will
        fail while the diagnostic is in progress. The diagnostic will take up to 5 minutes to complete.
      operationId: StartMoveToShelfDiagnostic
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveToShelfTest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/self-test:
    post:
      summary: Start a Library Self Test
      description: Start a Library Self Test.
      operationId: StartLibrarySelfTest
      tags: [ Cube ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/library/diagnostics/self-test/{taskID}':
    parameters:
      - $ref: '#/components/parameters/taskID'
    get:
      summary: Retrieve Specified Self Test
      description: |-
        Retrieve the information for a self test with a specified ID.
      operationId: GetLibrarySelfTestStatus
      tags: [ Cube ]
      x-permitted-roles: [ Admin, Operator, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibrarySelfTest'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/move-to-drives:
    post:
      summary: Start a Move To Drives diagnostic
      description: -|
        This test moves a tape to and from the specified drive(s). Calibrations are performed, if needed to perform the move. The tape
        used will be randomly selected from the partition to which the specified drive belongs. If the drive is in the free pool,
        the tape selected will be from the set of tapes in the free pool that are compatible with the selected drive.
      operationId: StartMoveToDrivesDiagnostic
      tags: [ Cube, TFinity ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                moves:
                  description: A list of move to drive diagnostics to perform.
                  type: array
                  minItems: 1
                  items:
                    $ref: '#/components/schemas/MoveToDrive'
              required:
                - moves
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/bulk-tap:
    post:
      summary: Start a Bulk TAP diagnostic
      description: -|
        This test will verify the operations of the bulk TAP.
      operationId: StartBulkTapDiagnostic
      tags: [ TFinity ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                side:
                  $ref: '#/components/schemas/BulkTAP'
              required:
                - side
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/security-audit:
    post:
      summary: Start a Security Audit diagnostic
      description: -|
        This diagnostic verifies magazine and tape barcodes, and the position of magazines and tapes in the library.
      operationId: StartLibrarySecurityAudit
      tags: [ Cube, TFinity ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/diagnostics/verify-magazine-barcodes:
    post:
      summary: Verify TeraPack magazine barcodes.
      description: -|
        This diagnostics scans the full library and checks all discovered magazines against stored inventory. Any moved
        or added magazine is pulled and its tapes are scanned. The verification process takes a minimum of 1.5 minutes
        per frame, during which time the robot is unavailable. NOTE - This diagnostic only verifies the inventory of
        tapes within the magazines that were moved or added since magazines were last discovered and scanned.
      operationId: StartVerifyMagazineBarcodesDiagnostic
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/library/diagnostics/reset-geometry':
    post:
      summary: Reset Library Geometry
      description: -|
        This utility resets the calibration of each drive/chamber so the robotics code will recalibrate the drive/chamber
        position the next time it is accessed. Frame calibrations will be preserved. Remove all tapes from tape drives
        before running this utility, since any loaded tapes will be inaccessible after running this utility. On non-Python
        libraries, some chambers will be automatically re-calibrated and Motion will be restarted after the reset. Motion will
        not be restarted on Python libraries.
      operationId: StartResetGeometry
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/library/diagnostics/{taskID}/abort':
    parameters:
      - $ref: '#/components/parameters/taskID'
    put:
      summary: Abort a Library Diagnostic.
      description: Request to abort a library diagnostic. The abort operation is
        best effort; there is no guarantee that the abort will succeed.
      operationId: AbortLibraryDiagnostic
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/library/diagnostics/basic-motion/{test}':
    parameters:
      - description: Basic Motion Test to Run
        name: test
        in: path
        required: true
        schema:
          $ref: '#/components/schemas/BasicMotionTest'
    post:
      summary: Start a Basic Motion Test diagnostic
      description: -|
        The specified basic motion test will be performed; for more information about the tests, see the "BasicMotionTest" schema description.
      operationId: StartBasicMotionTest
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /library/status:
    get:
      summary: Retrieve Current Library Status
      description: Retrieve the general status of library hardware and software.
      operationId: GetLibraryStatus
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryStatus'
        default:
          $ref: '#/components/responses/default'
  /licenses:
    get:
      summary: Retrieve Licenses
      description: Retrieve a list of licenses currently installed on the library.
      operationId: Licenses
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/License'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add a License
      description: Add a license on the library.
      operationId: AddLicense
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - licenseKey
              properties:
                licenseKey:
                  $ref: '#/components/schemas/LicenseKey'
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/License'
        default:
          $ref: '#/components/responses/default'
  /logs:
    get:
      summary: Retrieve Gathered Logs
      description: Retrieve a list of gathered log sets currently stored on the library. Results are in ascending order, sorted by the start time of the log gather. Log gather requests that have not completed are displayed first and are in ascending order by task start time. This endpoint is now deprecated, use /logs/download instead
      operationId: GetLogs
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      deprecated: true
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LogList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Begin Gathering Requested Logs
      description: Starts bundling logs for the given type or all types. This endpoint is now deprecated, use /logs/download instead
      operationId: StartLogGather
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      deprecated: true
      parameters:
        - description: Types of Logs to Gather. Available types are returned in the response from `GET /logs/types`.
            Leaving this query parameter empty results in gathering all log types except dip-e:adt.
            Gathered logsets are kept for 12 hours and then deleted.
          name: logType
          in: query
          schema:
            $ref: '#/components/schemas/LogTypes'
          explode: false
          examples:
            CAN:
              value: [ 'can' ]
              description: Get CAN logs
            Motion:
              value: [ 'motion' ]
              description: Get Motion logs
            Dip-e:
              value: [ 'dip-e' ]
              description: Get Dip-e logs
            LogLib:
              value: [ 'loglib' ]
              description: Get LogLib logs
            Lumos:
              value: [ 'lumos' ]
              description: Get Lumos logs
            SQL:
              value: [ 'mysql' ]
              description: Get MySQL server logs
            O/S:
              value: [ 'os' ]
              description: Get O/S logs
            All:
              value: [ ]
              description: Get all log types
            Multiple:
              value: [ 'can', 'motion', 'loglib' ]
              description: Get multiple types of logs
            Subtype:
              value: [ 'dip-e:adt' ]
              description: Get Dip-e ADT logs
        - description: Start Date to Gather Logs.  Defaults to 'now - 24 hours' if not supplied. Start date cannot occur after the current or end date.
          name: startTime
          in: query
          schema:
            type: string
            format: date-time
            example: "2020-12-03T23:59:59Z"
        - description: End Date to Gather Logs. Defaults to 'now' if not supplied or set in the future. End date cannot occur before the start date.
          name: endTime
          in: query
          schema:
            type: string
            format: date-time
          example: "2020-12-04T23:59:59Z"
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /logs/download:
    get:
      summary: Gather and save library logs
      description: Begin a log gather task and immediately save the generated logs
      operationId: DownloadLogsSynchronous
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: Types of Logs to Gather. Available types are returned in the response from `GET /logs/types`.
            Leaving this query parameter empty results in gathering all log types except dip-e:adt.
          name: logType
          in: query
          schema:
            $ref: '#/components/schemas/LogTypes'
          explode: false
          examples:
            CAN:
              value: [ 'can' ]
              description: Get CAN logs
            Motion:
              value: [ 'motion' ]
              description: Get Motion logs
            Dip-e:
              value: [ 'dip-e' ]
              description: Get Dip-e logs
            LogLib:
              value: [ 'loglib' ]
              description: Get LogLib logs
            Lumos:
              value: [ 'lumos' ]
              description: Get Lumos logs
            SQL:
              value: [ 'mysql' ]
              description: Get MySQL server logs
            O/S:
              value: [ 'os' ]
              description: Get O/S logs
            All:
              value: [ ]
              description: Get all log types
            Multiple:
              value: [ 'can', 'motion', 'loglib' ]
              description: Get multiple types of logs
            Subtype:
              value: [ 'dip-e:adt' ]
              description: Get Dip-e ADT logs
        - description: Start Date to Gather Logs.  Defaults to 'now - 24 hours' if not supplied. Start date cannot occur after the current or end date.
          name: startTime
          in: query
          schema:
            type: string
            format: date-time
            example: "2020-12-03T23:59:59Z"
        - description: End Date to Gather Logs. Defaults to 'now' if not supplied or set in the future. End date cannot occur before the start date.
          name: endTime
          in: query
          schema:
            type: string
            format: date-time
          example: "2020-12-04T23:59:59Z"
        - description: Save the gathered logs to all USBs connected to the LS
          name: saveToUSBs
          in: query
          schema:
            type: boolean
      responses:
        '200':
          description: OK
          content:
            application/x-gzip:
              schema:
                type: string
                format: binary
        default:
          $ref: '#/components/responses/default'
  /logs/types:
    get:
      summary: Retrieve a List of Available Log Types
      description: Returns a list of components running on the library that generate logs
      operationId: GetLogTypeList
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                additionalProperties:
                  type: array
                  items:
                    type: string
                example:
                  can: [ "app", "canA", "canC" ]
                  dip-e: [ "adt", "app" ]
                  drive: [ "trace" ]
                  loglib: [ "app" ]
                  lumos: [ "app", "config", "messages", "security", "web" ]
                  motion: [ "app", "config" ]
                  os: [ "kernel", "system" ]
        default:
          $ref: '#/components/responses/default'
  '/logs/{taskID}':
    parameters:
      - $ref: '#/components/parameters/taskID'
    get:
      summary: Retrieve a Gathered Logset
      description: Retrieve a previously Gathered Logset created through `POST /logs`. Created logsets are kept for 12 hours and then deleted. This endpoint is now deprecated, use /logs/download instead.
      operationId: GetLogsInfo
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      deprecated: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Log'
              example:
                $ref: '#/components/schemas/Log/example'
        default:
          $ref: '#/components/responses/default'
  '/logs/{taskID}/download':
    parameters:
      - $ref: '#/components/parameters/taskID'
    get:
      operationId: DownloadLogs
      summary: Download Specified Logset
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      deprecated: true
      description: Download logset. Filename format is <LibrarySerialNumber>_<EndTime>.tar.gz. If the library serial number cannot be retrieved, the filename defaults to FFFFFFFF.tar.gz. This endpoint is now deprecated, use /logs/download instead.
      responses:
        '200':
          description: OK
          content:
            application/x-gzip:
              schema:
                type: string
                format: binary
        default:
          $ref: '#/components/responses/default'
  /magazines:
    get:
      summary: Retrieve TeraPack Magazine Information
      description: Retrieve a list of TeraPack magazines in the library.
      operationId: GetMagazines
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - name: state
          in: query
          description: Returns magazines filtered by accessible or inaccessible. By default, magazines are not filtered by accessibility.
          schema:
            $ref: '#/components/schemas/ElementStateType'
        - name: pool
          in: query
          description: Returns magazines in the given chamber pool. By default, all pools will be searched.
          schema:
            $ref: '#/components/schemas/PoolType'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MagazineList'
        default:
          $ref: '#/components/responses/default'
  '/magazines/{barcode}':
    parameters:
      - description: The barcode of the TeraPack magazine. Use the command `GET /magazines` to view a list of magazine barcodes.
        name: barcode
        in: path
        required: true
        schema:
          type: string
        example: "LUE0Q3X"
    get:
      summary: Retrieve information for a Single TeraPack Magazine
      description: Retrieve information of a single TeraPack magazine with the specified barcode.
      operationId: GetMagazine
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Magazine'
        default:
          $ref: '#/components/responses/default'
  /magazines/free-pool:
    get:
      summary: Retrieve Free Pool TeraPack Magazines
      description: Retrieve a list of TeraPack magazines assigned to the free pool.
      operationId: GetFreePoolMagazines
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FreePoolMagazineList'
        default:
          $ref: '#/components/responses/default'
  /messages:
    get:
      summary: Retrieve Status Messages
      description: |-
        Retrieve a list of status messages from the library
      operationId: GetMessages
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: ID of the messages to retrieve. These values can be found from the result of `GET /messages`.
          in: query
          name: id
          schema:
            type: string
            example: "DCM_1_POLL_FAILED_MSG_NUM"
        - description: |-
            Filters for messages created after the specified time. Defaults to no filter.
          in: query
          name: startTime
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
        - description: |-
            Filters for messages created before the specified time. Defaults to no filter.
          in: query
          name: endTime
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
        - description: |-
            Filters for messages based on read status. Defaults to no filter.
          in: query
          name: read
          schema:
            type: boolean
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatusMessageList'
        default:
          $ref: '#/components/responses/default'
  /messages/set-read:
    put:
      summary: Set Messages as read or unread.
      description: Set message read state.
      operationId: SetReadForMessages
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                uids:
                  description: A list of message UIDs to change.
                  type: array
                  items:
                    type: string
                read:
                  type: boolean
              required:
                - uids
                - read
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /metrics/media-moves:
    get:
      summary: Retrieve media move metrics
      description: Retrieve time series data for media moves. Moves are summed into time buckets, which default to 1 hour each of the last 24 hours.
      operationId: GetMediaMoveMetrics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      x-experimental: true
      parameters:
        - description: |-
            First bucket will start at the specified time. Defaults to 24 hours ago. The time must not exceed one year in the past.
          in: query
          name: startTime
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
        - description: |-
            Last bucket will end at the specified time. Defaults to the current time. Time must be after the Unix epoch of 1970-01-01T00:00:00Z
          in: query
          name: endTime
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
        - description: |-
            Moves will be summed into time buckets of this size. Defaults to 1 hour. The interval must be at least 1 hour when providing a time range of more than 30 days.
          in: query
          name: interval
          schema:
            $ref: '#/components/schemas/TimeInterval'
        - description: |-
            Filters for moves based on the source container type for the move. Defaults to all types.
          name: sourceType
          in: query
          schema:
            $ref: '#/components/schemas/ContainerTypes'
          example: "SLOT"
        - description: |-
            Filters for moves based on the destination container type for the move. Defaults to all types.
          name: destinationType
          in: query
          schema:
            $ref: '#/components/schemas/ContainerTypes'
          example: "DRIVE"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaMoveMetrics'
        default:
          $ref: '#/components/responses/default'
  /metrics/library/temperature:
    get:
      summary: Retrieve temperature metrics
      description: Retrieve time series data for the temperature sensors on the robotics or the library chassis. Temperature is averaged into time buckets, which default to 1 hour each of the last 24 hours. Measurements are returned in degrees Celsius.
      operationId: GetTemperatureMetrics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      x-experimental: true
      parameters:
        - name: startTime
          in: query
          description: First bucket will start at the specified time. Defaults to 24 hours ago. The time must not exceed one year in the past.
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: endTime
          in: query
          description: Last bucket will end at the specified time. Defaults to the current time. Time must be after the Unix epoch of 1970-01-01T00:00:00Z
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: interval
          description: |-
            Temperature will be averaged into time buckets of this size. Defaults to 1 hour, and must be at least 10 minutes. The interval must be at least 1 hour when providing a time range of more than 30 days.
          in: query
          schema:
            $ref: '#/components/schemas/TimeInterval'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryTemperatureMetrics'
        default:
          $ref: '#/components/responses/default'
  /metrics/library/humidity:
    get:
      summary: Retrieve humidity metrics
      description: Retrieve time series data for the humidity sensors on the robotics or the library chassis. The data is averaged into time buckets, which default to 1 hour each of the last 24 hours. Measurements are returned in percent relative humidity.
      operationId: GetHumidityMetrics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      x-experimental: true
      parameters:
        - name: startTime
          in: query
          description: First bucket will start at the specified time. Defaults to 24 hours ago. The time must not exceed one year in the past.
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: endTime
          in: query
          description: Last bucket will end at the specified time. Defaults to the current time. Time must be after the Unix epoch of 1970-01-01T00:00:00Z
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: interval
          description: |-
            Humidity will be averaged into time buckets of this size. Defaults to 1 hour, and must be at least 10 minutes. The interval must be at least 1 hour when providing a time range of more than 30 days.
          in: query
          schema:
            $ref: '#/components/schemas/TimeInterval'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryHumidityMetrics'
        default:
          $ref: '#/components/responses/default'
  /metrics/power-consumption:
    get:
      summary: Retrieve power consumption metrics
      description: Retrieve time series data for the power consumption on the library or individual controller.
      operationId: GetPowerConsumptionMetrics
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - name: startTime
          in: query
          description: First bucket will start at the specified time. Defaults to 24 hours ago. The time must not exceed one year in the past.
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: endTime
          in: query
          description: Last bucket will end at the specified time. Defaults to the current time. Time must be after the Unix epoch of 1970-01-01T00:00:00Z
          schema:
            type: string
            format: date-time
            example: "2006-01-02T15:04:05Z"
        - name: interval
          in: query
          description: Readings will be averaged into time buckets of this size. Defaults to 1 hour. The interval must be at least 1 hour when providing a time range of more than 30 days.
          schema:
            $ref: '#/components/schemas/TimeInterval'
        - description: |-
            Source of the power reading, or "Lumos" for the entire library. Defaults to no filter.
            Other possible sources are FMM, PCM, or PMM FRU names.
          in: query
          name: source
          schema:
            type: string
            example: "Lumos"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PowerConsumptionList'
        default:
          $ref: '#/components/responses/default'
  /mlm-records:
    get:
      summary: Retrieve MLM Data
      description: |-
        Retrieve a list of Media Lifecycle Management (MLM) data from the library.
      operationId: GetMLM
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - $ref: '#/components/parameters/barcodeParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MLMList'
              examples:
                mlmList:
                  $ref: '#/components/examples/mlmList'
        default:
          $ref: '#/components/responses/default'
  /mlm-records/{serialNumber}:
    parameters:
      - description: Serial number of a tape for which to retrieve MLM data. This is returned as `serialNumber` in the response from `GET /mlm`.
        in: path
        name: serialNumber
        schema:
          type: string
        required: true
        example: PCK2022165
    get:
      summary: Retrieve MLM Data for a Specified Tape
      description: |-
        Retrieve the MLM data for the tape with the specified serial number.
      operationId: GetMLMRecord
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MLMRecord'
              examples:
                data:
                  $ref: '#/components/examples/mlmDataDataTape'
                cleaning:
                  $ref: '#/components/examples/mlmDataCleaningTape'
        default:
          $ref: '#/components/responses/default'
  /mlm-records/{serialNumber}/history:
    parameters:
      - description: Serial number of a tape for which to retrieve MLM data. This is returned as `serialNumber` in the response from `GET /mlm`.
        in: path
        name: serialNumber
        schema:
          type: string
        required: true
        example: PCK2022165
      - $ref: '#/components/parameters/offsetParam'
      - $ref: '#/components/parameters/limitParam'
    get:
      summary: Retrieve MLM load history records for a Specified Tape
      description: |-
        Retrieve the MLM load history data for the tape with the specified serial number.
      operationId: GetMLMLoadHistory
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoadHealthHistory'
        default:
          $ref: '#/components/responses/default'
  /quick-post-scan/queue:
    get:
      summary: Retrieve QuickPostScan Queue.
      description: |-
        Retrieve a list of all tapes that are currently queued for QuickPostScan.
      operationId: GetQuickPostScanQueue
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QuickPostScanQueue'
        default:
          $ref: '#/components/responses/default'
  /moves/clean:
    post:
      summary: Clean a Drive
      description: |-
        Clean the specified drive. The drive's storage partition must have an associated cleaning partition.
        The cleaning tape will be chosen at random from the storage partition's associated cleaning partition.
        This operation will move the cleaning tape to and from the drive and will send an inventory update to all exporters
        when the tape is moved to/from the drive. The cleaning operation will be recorded in the library's cleaning move history.
      operationId: StartDriveCleanMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestClean'
        required: true
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
    get:
      summary: Retrieve Clean Moves
      description: |-
        Retrieve a list of manual and interim clean moves.
      operationId: GetCleanMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: The serial number assigned to the physical drive by the drive manufacturer.
          required: false
          in: query
          name: driveManufacturerSerial
          schema:
            type: string
          example: "10WT049947"
        - description: The name of the storage partition associated with the cleaning move.
          required: false
          in: query
          name: storagePartition
          schema:
            type: string
          example: "Storage"
        - description: The name of the cleaning partition associated with the cleaning move.
          required: false
          in: query
          name: cleaningPartition
          schema:
            type: string
          example: "Cleaning"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CleanMoveList'
        default:
          $ref: '#/components/responses/default'
  /moves/import:
    get:
      summary: Retrieve Import Moves
      description: |-
        Retrieve a list of all active, queued, and stopped import moves.
      operationId: GetImportMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ImportMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add import move
      description: |-
        Add an import move to the move queue. Operators may only import to ENTRY_EXIT pools.
      operationId: StartImportMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestImport'
        required: true
      responses:
        '202':
          description: Returns a task ID for each full import chamber in the provided tap
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskIdList'
        default:
          $ref: '#/components/responses/default'
  /moves/export:
    get:
      summary: Retrieve Export Moves
      description: |-
        Retrieve a list of all active, queued, and stopped export moves.
      operationId: GetExportMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExportMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add export move
      description: |-
        Add an export move to the move queue. Operators may only export from ENTRY_EXIT pools.
      operationId: StartExportMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestExport'
        required: true
      responses:
        '202':
          description: Returns a task ID for each provided magazine
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskIdList'
        default:
          $ref: '#/components/responses/default'
  /moves/media:
    get:
      summary: Retrieve Media Moves
      description: |-
        Retrieve a list of all active, queued, and stopped media moves.
      operationId: GetMediaMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add media move
      description: |-
        Add a media move to the move queue
      operationId: StartMediaMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestMedia'
        required: true
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /moves/assign-to-partition:
    get:
      summary: Retrieve magazine partition assignment moves
      description: |-
        Retrieve a list of all active, queued, and stopped magazine partition assignment moves.
      operationId: GetPartitionAssignMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PartitionAssignMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add magazine partition assignment move
      description: |-
        Add a move to assign a magazine to a partition.
      operationId: StartPartitionAssignMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestPartitionAssign'
        required: true
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /moves/assign-to-free-pool:
    get:
      summary: Retrieve magazine free pool assignment moves
      description: |-
        Retrieve a list of all active, queued, and stopped magazine free pool assignment moves.
      operationId: GetFreePoolAssignMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FreePoolAssignMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add magazine free pool assign move
      description: |-
        Add a move to assign a magazine to the free pool.
      operationId: StartFreePoolAssignMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestFreePoolAssign'
        required: true
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /encryption/recycle-encrypted-media:
    get:
      summary: Retrieve Recycle Encrypted Media Moves
      description: |-
        Retrieve a list of all active, queued, and stopped recycle encrypted media moves.
      operationId: GetRecycleEncryptedMediaMoves
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - $ref: '#/components/parameters/partition'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: Task ID of a move
          required: false
          in: query
          name: taskID
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaMoveList'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Add recycle encrypted media move
      description: |-
        This operation will add a move that will recycle encrypted media to the move queue. Recycling encrypted media
        will remove drive based encryption keys from the media, which will restore the ability for drives to read/write
        unencrypted data or use a new key. This move must use a drive as the destination.
        WARNINGS: This operation may render the tape's data unrecoverable.  This operation will remove the encryption
        keys, but not the data. You will need to additionally erase the tape with your host software to allow the tape
        to be reused without encryption or with a new encryption key. See the Spectra Logic Encryption Users' guide for complete details.
      operationId: StartRecycleEncryptedMediaMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MoveRequestMedia'
        required: true
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/moves/{taskID}/abort':
    parameters:
      - $ref: '#/components/parameters/taskID'
    put:
      summary: Abort a Queued Move.
      description: |-
        Request to abort a move.  Depending on the state of the move, the abort request may not succeed.
        Currently, only moves in the 'PENDING' state can be aborted.
      operationId: AbortMove
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /packages:
    get:
      summary: Retrieve Available Packages
      description: |-
        Retrieve a list of update packages on the library.
      operationId: GetPackages
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PackageList'
        default:
          $ref: '#/components/responses/default'
  /packages/upload:
    post:
      summary: Upload Package
      description: |-
        Upload a new software package to the library.
      operationId: UploadPackage
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                packageFile:
                  type: string
                  format: binary
                pubkeyFile:
                  type: string
                  format: binary
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Package'
        default:
          $ref: '#/components/responses/default'
  '/packages/active':
    get:
      summary: Show Active Package
      description: |-
        Show information about the currently active software package on the library.
      operationId: GetActivePackage
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Package'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Active Package
      description: |-
        Updates the library to the specified software package.
        Note: Your library must either still be under warranty or you must have a current service contract with
        Spectra Logic Technical Support before you can perform package updates.

        A package update can take a large amount of time. The library cannot be used until the update completes.
        Once started, the update can not be canceled.
      operationId: StartLibraryUpdate
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PackageUpdateRequest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  '/packages/{name}':
    get:
      summary: Get Package By Name
      description: Retrieves the package information associated with the name provided
      operationId: GetPackageByName
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - description: Name of a package. This is returned as 'name' in the response for GET /packages.
          required: true
          name: name
          in: path
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Package'
              examples:
                full:
                  value:
                    $ref: '#/components/schemas/Package/example'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a package by name
      description: Deletes the package with the specified name
      operationId: DeletePackage
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: Name of package. This is returned as 'name' in the response for GET /packages.
          required: true
          name: name
          in: path
          schema:
            type: string
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /packages/state:
    get:
      summary: Get Current Update State
      description: |-
        Get the state of the current update. This endpoint is now deprecated, use the /tasks endpoint to find the state of the latest package update.
      operationId: GetPackageUpdateState
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      deprecated: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PackageState'
        default:
          $ref: '#/components/responses/default'
  /partitions:
    delete:
      summary: Delete all Partitions
      description: |-
        Delete all library partitions. This will cause a full library reboot. The partitions are automatically recreated on libraries that support automatic partitions.
      operationId: StartDeleteAllPartitions
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
    get:
      summary: Retrieve Partitions
      description: |-
        Retrieve a list of all logical partitions that exist on the library.
      operationId: GetPartitions
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Partition'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Create a partition
      description: Create a partition on the library.
      operationId: CreatePartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreatePartitionRequest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /partitions/{partition}:
    parameters:
      - description: Name of the partition. This is returned as `name` from `GET /partitions`.
        required: true
        name: partition
        in: path
        schema:
          type: string
          example: "Data Partition"
    get:
      summary: Retrieve Specified Partition
      description: |-
        Retrieve information about a partition with the specified name.
      operationId: GetPartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Partition'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a Partition
      description: |-
        Delete the partition with the specified name.
      operationId: DeletePartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update the Specified Partition
      description: |-
        Update information about a partition with the specified name.
      operationId: UpdatePartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdatePartitionRequest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /partitions/cleaning:
    get:
      summary: Retrieve Cleaning Partitions
      description: |-
        Retrieve a list of all logical cleaning partitions that exist on the library.
      operationId: GetCleaningPartitions
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CleaningPartition'
        default:
          $ref: '#/components/responses/default'
    post:
      summary: Create a cleaning partition
      description: Create a cleaning partition on the library.
      operationId: CreateCleaningPartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateCleaningPartitionRequest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /partitions/cleaning/{partition}:
    parameters:
      - description: Name of the cleaning partition. This is returned as `name` from `GET /partitions/cleaning`.
        required: true
        name: partition
        in: path
        schema:
          type: string
          example: "Cleaning Partition"
    get:
      summary: Retrieve Specified Cleaning Partition
      description: |-
        Retrieve information about a cleaning partition with the specified name.
      operationId: GetCleaningPartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CleaningPartition'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a Cleaning Partition
      description: |-
        Delete the cleaning partition with the specified name. A cleaning partition cannot be deleted if it is associated with a storage partition.
      operationId: DeleteCleaningPartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update the Specified Cleaning Partition
      description: |-
        Update information about a cleaning partition with the specified name.
      operationId: UpdateCleaningPartition
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateCleaningPartitionRequest'
      responses:
        '202':
          $ref: '#/components/responses/202'
        default:
          $ref: '#/components/responses/default'
  /settings/auth:
    get:
      summary: Retrieve Authorization Settings
      description: |-
        Retrieve the current and default values of the library authorization settings. Multiple ldap authenticators can be configured, but only one native authenticator can be configured at a time.
      operationId: GetAuthSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Settings
      description: |-
        Set the values of all library authorization settings.
      operationId: SetAuthSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AuthSettings'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/auth/local-users:
    get:
      summary: Retrieve a List of All Native Authentication Users
      description: Retrieve a list of all users defined in the Native Authentication server
      operationId: GetUsers
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - description: |-
            Returns users with access to the specified partition
          name: partition
          in: query
          schema:
            type: string
        - description: |-
            Returns users belonging to the specified group
          name: group
          in: query
          schema:
            $ref: '#/components/schemas/GroupNames'
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
        default:
          $ref: '#/components/responses/default'
  /settings/auth/local-users/{userName}:
    parameters:
      - description: Username for user to retrieve or to delete
        name: userName
        in: path
        required: true
        schema:
          type: string
    get:
      summary: Retrieve Information about the Specified Native Authentication User
      description: Retrieve information about a Native Authentication user with the specified username
      operationId: GetUser
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a Native Authentication User
      description: Deletes the specified user from the Native Authentication server
      operationId: DeleteUser
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Edit Native Authentication User Settings
      description: Changes the specified user’s group and/or partitions settings in the Native Authentication server
      operationId: UpdateUser
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserChangeRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/auth/local-users/{userName}/change-password:
    parameters:
      - description: Username of the user for which you want to change the password.
        name: userName
        in: path
        required: true
        schema:
          type: string
    put:
      summary: Change a User Password
      description: Change the password for the specified user in the Native Authentication server.
      operationId: UserPasswordChange
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserPasswordChangeRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/auth/local-users/create:
    post:
      summary: Create a New User in the Native Authentication Server
      description: Creates a new user within the Native Authentication server
      operationId: CreateUser
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRequest'
        required: true
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        default:
          $ref: '#/components/responses/default'
  /settings/backups:
    get:
      summary: Retrieve Backup Settings
      description: |-
        Retrieve the current and default values of the library backup settings.
      operationId: GetBackupSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BackupSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Backup Settings
      deprecated: true
      description: |-
        Deprecated - use UpdateBackupSettings instead. Set the values of all library backup settings.
      operationId: SetBackupSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BackupSettings'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update Backup Settings
      description: |-
        Update the library's backup settings
      operationId: UpdateBackupSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateBackupSettingsRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/barcode:
    get:
      summary: Retrieve Barcode Settings
      description: Retrieve the current and default values of the library-wide tape barcode options used by all partitions.
      operationId: GetGlobalMediaBarcodeSettings
      tags: [ Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BarcodeOptions'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Edit Barcode Settings.
      description: Set the library-wide tape barcode options used by all partitions. Upon changing these settings, the robotics will reinitialize. If "checksumBehavior" is changed, the library's inventory will additionally have to be rescanned. In either case, the robotics will be available again when the "state" from /library/status becomes "READY".
      operationId: SetGlobalMediaBarcodeSettings
      tags: [ Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BarcodeOptions'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/encryption/authorization:
    get:
      summary: Get encryption authorization settings.
      description: Retrieve the current encryption authorization settings configured on the library.
      operationId: GetEncryptionAuthorizationSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EncryptionAuthorizationSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Edit the encryption authorization settings.
      description: Change the active encryption authorization settings for the library.
      operationId: SetEncryptionAuthorizationSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          description: Authorization required to change encryption settings. An empty password must be used during
            initial setup when the encryption authorization passwords have not been initialized.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
        - name: Secondary-Encryption-Authorization
          in: header
          description: Additional authorization required in multi user mode.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                mode:
                  $ref: "#/components/schemas/EncryptionMode"
                authorization:
                  $ref: "#/components/schemas/EncryptionAuthorizationPassword"
                  description: Authorization required to change encryption settings. An empty password must be used during
                    initial setup when the encryption authorization passwords have not been initialized. Only one password is required
                    in single user mode. This field may not be used in conjunction with `MULTI_USER` mode and the `Encryption-Authorization`
                    header must be used to provide the required passwords.
                  deprecated: true
                updatedAuthorizationPasswords:
                  type: array
                  minItems: 1
                  items:
                    $ref: '#/components/schemas/EncryptionAuthorizationPassword'
                  description: Passwords to be used to authorize encryption operations. Only one password may be
                    provided in single user mode. Three passwords must be provided in multi user mode. All passwords must be unique.
              required:
                - mode
                - updatedAuthorizationPasswords
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/encryption/bluescale:
    get:
      summary: Get BlueScale encryption settings.
      description: Retrieve the current BlueScale encryption settings configured on the library.
      operationId: GetBlueScaleEncryptionSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BlueScaleEncryptionSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Edit the BlueScale encryption settings.
      description: Change the active BlueScale encryption settings for the library.
      operationId: SetBlueScaleEncryptionSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      parameters:
        - name: Encryption-Authorization
          in: header
          description: Authorization required to change encryption settings. An empty password must be used during
            initial setup when the encryption authorization passwords have not been initialized.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
        - name: Secondary-Encryption-Authorization
          in: header
          description: Additional authorization required in multi user mode.
          schema:
            $ref: '#/components/schemas/EncryptionAuthorizationPassword'
          example: "password"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                settings:
                  $ref: "#/components/schemas/BlueScaleEncryptionSettings"
                authorization:
                  $ref: "#/components/schemas/EncryptionAuthorizationPassword"
                  description: Authorization required to change encryption settings. An empty password must be used during
                    initial setup when the encryption authorization passwords have not been initialized. Only one password is required
                    in single user mode. This field may not be used in conjunction with `MULTI_USER` mode and the `Encryption-Authorization`
                    header must be used to provide the required passwords.
                  deprecated: true
              required:
                - settings
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/library:
    get:
      summary: Retrieve Basic Settings
      description: |-
        Retrieve the current and default values of the library basic settings.
      operationId: GetBasicSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BasicSettingsResponse'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Basic Settings
      description: |-
        Deprecated - use UpdateBasicSettings instead. Set the values of all library basic settings.
      operationId: SetBasicSettings
      deprecated: true
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BasicSettings'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update Basic Settings
      description: |-
        Update the values of library basic settings.
      operationId: UpdateBasicSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateBasicSettingsRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/network:
    get:
      summary: Retrieve Network Settings
      description: |-
        Retrieve the current and default values of the library network settings.
      operationId: GetNetworkSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NetworkSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Network Settings
      deprecated: true
      description: |-
        Deprecated - use UpdateNetworkSettings instead. Set the values of all library network settings.
      operationId: SetNetworkSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NetworkSettings'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update Network Settings
      description: |-
        Set the values of all library network settings.
      operationId: UpdateNetworkSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateNetworkSettingsRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/power:
    get:
      summary: Retrieve Library Power Settings
      description: Retrieve the library power settings.
      operationId: GetPowerSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PowerSettings'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update Library Power Settings
      description: Update the library power settings
      operationId: UpdatePowerSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdatePowerSettingsRequest'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/remote-access:
    get:
      summary: Retrieve Remote Access Settings
      description: |-
        Retrieve the current values of the remote access settings.
      operationId: GetRemoteAccessSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RemoteAccessSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Remote Access Settings
      description: |-
        Set the values of remote access settings. Remote access settings are not guaranteed to persist across package updates or backup restores. All changes made via SSH such as changing passwords is not guaranteed to persist across package updates or backup restores.
      operationId: SetRemoteAccessSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RemoteAccessSettings'
        required: true
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/remote-client:
    get:
      summary: Get Remote Client Settings
      description: Get the settings concerning remote clients of the LumOS API.
      operationId: GetRemoteClientSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/defaultSettingParam'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RemoteClientSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Remote Client Settings
      description: Set the settings concerning remote clients of the LumOS API.
      operationId: SetRemoteClientSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RemoteClientSettings'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/startup-scan:
    get:
      summary: Retrieve Startup Scan Settings
      description: |-
        Retrieve the current value of the library startup scan setting. This setting determines what type of scan the robot will perform
        when the library is powered on or the door is opened and closed.
      operationId: GetStartupScanMode
      tags: [ Cube ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StartupScanSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Startup Scan Settings
      description: |-
        Set the value of the library startup scan setting. This setting determines what type of scan the robot will perform
        when the library is powered on or the door is opened and closed. Changes to this setting will take effect the next time
        the library is restarted.
      operationId: SetStartupScanMode
      tags: [ Cube ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/StartupScanSettings'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/syslog:
    get:
      summary: Retrieve Syslog Settings
      description: |-
        Retrieve the current value of the library syslog settings.
      operationId: GetSyslogSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SyslogSettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Syslog Settings
      description: |-
        Set the value of the library syslog settings.
      operationId: SetSyslogSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SyslogSettings'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /settings/tls/certificate:
    put:
      summary: Upload Certificate and Key File
      description: |-
        Upload a certificate and key file to use for the library TLS configuration. This action
        restarts the web server, which aborts active requests and briefly causes the library to reject new requests.
      operationId: UploadCertificate
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ SuperUser ]
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                key:
                  type: string
                  format: binary
                cert:
                  type: string
                  format: binary
              required:
                - key
                - cert
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /summary/capacity/chambers:
    get:
      summary: Retrieve Library Chamber Capacity Summary
      description: |-
        Retrieve a breakdown of library chamber capacity
      operationId: GetChamberCapacitySummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryChamberCapacitySummary'
        default:
          $ref: '#/components/responses/default'
  /summary/settings:
    get:
      summary: Get Summary Settings
      description: |-
        Get the summary information that is available unauthenticated
      operationId: GetSummarySettings
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SummarySettings'
        default:
          $ref: '#/components/responses/default'
    put:
      summary: Set Summary Settings
      description: |-
        Set the summary information that is available unauthenticated
      operationId: SetSummarySettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      x-experimental: true
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SummarySettings'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SummarySettings'
        default:
          $ref: '#/components/responses/default'
  /summary/drives:
    get:
      summary: Get a summary of drives.
      description: |-
        Get a summary of the drives in the library.
      operationId: GetDrivesSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DrivesSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/media:
    get:
      summary: Get a summary of media.
      description: |-
        Get a summary of media.
      operationId: GetMediaSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MediaSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/messages:
    get:
      summary: Get a summary of the status messages
      description: |-
        Get the total number of unread status messages, as well as the number of status messages grouped by severity from the library.
      operationId: GetMessagesSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MessageSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/environment:
    get:
      summary: Get a summary of temperature and humidity from library sensors
      description: |-
        Get the current values of the temperature and humidity from sensors in the library
      operationId: GetEnvironmentSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EnvironmentSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/power-consumption:
    get:
      summary: Get a summary of library power consumption
      description: |-
        Get the last 24 hours of the library's power consumption
      operationId: GetPowerConsumptionSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PowerConsumptionList'
        default:
          $ref: '#/components/responses/default'
  /summary/moves:
    get:
      summary: Get a summary of library moves.
      description: |-
        Get a summary of recent library move information.
      operationId: GetMovesSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MovesSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/robotics:
    get:
      summary: Get a summary of robotics.
      description: |-
        Get a summary of robotics.
      operationId: GetRoboticsSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RoboticsSummary'
        default:
          $ref: '#/components/responses/default'
  /summary/library-info:
    get:
      summary: Get a summary of library information.
      description: |-
        Get a summary of library information.
      operationId: GetLibraryInfoSummary
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      x-experimental: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LibraryInfoSummary'
        default:
          $ref: '#/components/responses/default'
  /subscriptions:
    post:
      summary: Add a New Subscriber
      description: |-
        Add a new subscriber to the library with a configured SMTP server. A maximum of 32 subscribers can be added.
      operationId: AddSubscriber
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Subscriber'
      responses:
        '201':
          description: Created
          headers:
            Location:
              $ref: '#/components/headers/Location'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Subscriber'
        default:
          $ref: '#/components/responses/default'
    get:
      summary: Get Current Subscribers
      description: |-
        Get a list of current subscribers
      operationId: GetSubscribers
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Subscriber'
        default:
          $ref: '#/components/responses/default'
  /subscriptions/{subscriberID}:
    parameters:
      - $ref: '#/components/parameters/subscriberID'
    get:
      summary: Get Subscriber
      description: |-
        Get information about a subscriber with ID subscriberID
      operationId: GetSubscriberByID
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Subscriber'
        default:
          $ref: '#/components/responses/default'
    patch:
      summary: Update the Specified Subscriber
      description: |-
        Update information about a subscriber with the specified ID.
      operationId: UpdateSubscriber
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateSubscriberRequest'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Subscriber'
        default:
          $ref: '#/components/responses/default'
    delete:
      summary: Delete a Subscriber
      description: Deletes a subscriber from the library
      operationId: DeleteSubscriber
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /subscriptions/{subscriberID}/test-email:
    parameters:
      - $ref: '#/components/parameters/subscriberID'
    post:
      summary: Send test email to Subscriber
      description: |-
        Send a test email to the subscriber with the specified ID.
      operationId: SendSubscriberTestEmail
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /subscriptions/generate-report:
    post:
      summary: Generate Critical Event Report
      description: |-
        Generate critical event report and send to all subscribers
      operationId: SendCriticalEventReport
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CriticalEventProblemDescription'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /subscriptions/settings:
    put:
      summary: Set the library subscription settings
      description: |-
        Set the library subscription settings
      operationId: SetSubscriptionSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SubscriptionSettings'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubscriptionSettings'
        default:
          $ref: '#/components/responses/default'
    get:
      summary: Get Subscription Settings
      description: |-
        Get subscription settings
      operationId: GetSubscriptionSettings
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubscriptionSettings'
        default:
          $ref: '#/components/responses/default'
  /taps:
    get:
      summary: Retrieve TAPs
      description: |-
        Retrieve a list of the library TeraPack Access Ports (TAPs).
      operationId: GetTAPs
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TAP'
        default:
          $ref: '#/components/responses/default'
  /taps/installed-types:
    get:
      summary: Retrieve Installed TAP Types
      description: |-
        Retrieve a list of the installed TeraPack Access Ports (TAPs) types.
      operationId: GetInstalledTAPTypes
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TAPTypes'
        default:
          $ref: '#/components/responses/default'
  '/taps/{name}':
    parameters:
      - $ref: '#/components/parameters/tapName'
    get:
      summary: Retrieve a TAP
      description: |-
        Retrieve information about the specified TAP
      operationId: GetTAP
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TAP'
        default:
          $ref: '#/components/responses/default'
  /taps/{name}/open:
    put:
      summary: Open a TAP door on a library
      description: |-
        Open a TAP door
      operationId: OpenTAP
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/tapName'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /taps/{name}/close:
    put:
      summary: Close a TAP door in a TFinity library
      description: |-
        Close a TAP door
      operationId: CloseTAP
      tags: [ TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/tapName'
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
  /tasks:
    get:
      summary: Retrieve Task Data
      description: |-
        Retrieves information about a specified task. If a time range is provided, all tasks at least partially within the given range are included. All users can access this endpoint, but only tasks
        that the user has permission to view are returned.
      operationId: GetTasks
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      parameters:
        - $ref: '#/components/parameters/offsetParam'
        - $ref: '#/components/parameters/limitParam'
        - description: |-
            Returns tasks in the specified state. If not included, all states are returned.
          name: state
          in: query
          schema:
            $ref: '#/components/schemas/TaskStates'
        - description: |-
            Deprecated. Use taskTypes instead.
            The type of tasks to return. If not included, all types are returned.
          name: taskType
          deprecated: true
          in: query
          schema:
            $ref: '#/components/schemas/TaskTypes'
        - name: taskTypes
          in: query
          explode: false
          description: |-
            A comma-separated list of task types to return. If not included, all types are returned.
          schema:
            type: array
            items:
              $ref: "#/components/schemas/TaskTypes"
        - description: |-
            Returns tasks with the specified tags. If not included, all tasks are returned.
          name: tag
          in: query
          schema:
            type: string
        - description: |-
            Filters for tasks completed after the specified time.
          name: startTime
          in: query
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
        - description: |-
            Filters for tasks started before the specified time.
          name: endTime
          in: query
          schema:
            type: string
            format: date-time
            example: "2017-07-21T17:32:28Z"
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskList'
        default:
          $ref: '#/components/responses/default'
  /tasks/{taskID}:
    parameters:
      - $ref: '#/components/parameters/taskID'
    get:
      summary: Retrieve Specified Task
      description: Retrieve information about a task specified by ID. All users can access this endpoint, but only tasks that the user has permission to view are returned.
      operationId: GetTask
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        default:
          $ref: '#/components/responses/default'
  /time:
    get:
      summary: Retrieve the current library time
      description: |-
        Returns the current time on the library.
      operationId: GetTime
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TimeResponse'
        default:
          $ref: '#/components/responses/default'
  /auth/login:
    post:
      summary: Request Authorization Token (JWT)
      description: Authenticates the user using the given credentials and returns a token accepted by the rest of the API. Set-Cookie headers are provided for web clients to store "Authorization" and "Authorization-Metadata" cookies. "Authorization" contains the token, while "Authorization-Metadata" contains a URL-encoded JSON object.
      operationId: Login
      tags: [ Cube, TFinity, Python ]
      security: [ ]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
        required: true
      responses:
        '200':
          description: OK
          headers:
            Set-Cookie:
              schema:
                $ref: '#/components/schemas/AuthorizationMetadata'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        default:
          $ref: '#/components/responses/default'
  /auth/refresh:
    post:
      summary: Refresh Authorization Token (JWT)
      description: Request to refresh an authorization token. A token can be refreshed only if neither its expiration date nor its refresh timeout date have passed. Set-Cookie headers are provided for web clients to store "Authorization" and "Authorization-Metadata" cookies.
      operationId: RefreshToken
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '200':
          description: OK
          headers:
            Set-Cookie:
              schema:
                $ref: '#/components/schemas/AuthorizationMetadata'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        default:
          $ref: '#/components/responses/default'
  /auth/logout:
    post:
      summary: Logout
      description: Request to invalidate an authorization token.
      operationId: Logout
      tags: [ Cube, TFinity, Python ]
      x-permitted-roles: [ Operator, Admin, SuperUser ]
      responses:
        '204':
          $ref: '#/components/responses/204'
        default:
          $ref: '#/components/responses/default'
components:
  parameters:
    backupName:
      description: The name of a backup file.
      required: true
      name: name
      in: path
      schema:
        title: backupName- The name of a backup file.
        type: string
        example: "0123456789_2023-04-12T213951Z.tar.gz"
    barcodeParam:
      description: The barcode of the tape cartridge
      required: false
      name: barcode
      in: query
      schema:
        type: string
        example: "000797L6"
    containerType:
      description: The type of media container.
        <table>
        <tr>
        <th><b>Type</b></th>
        <th>Description</th>
        </tr>
        <tr>
        <td>SLOT</td>
        <td>A regular slot in a TeraPack magazine</td>
        </tr>
        <tr>
        <td>IE_SLOT</td>
        <td>A slot in a TeraPack magazine that was assigned to an EE chamber</td>
        </tr>
        <tr>
        <td>DRIVE</td>
        <td>A physical drive</td>
        </tr>
        </table>
      name: containerType
      in: query
      schema:
        $ref: '#/components/schemas/ContainerTypes'
      example: "SLOT"
      required: false
    defaultSettingParam:
      description: Return default value.  When provided, the library returns the default value for the setting instead of the current value.
      name: defaults
      in: query
      schema:
        type: boolean
        default: false
    fruName:
      description: Name of the field replaceable unit to retrieve. This is returned as `name` in the response from `GET /frus`.
      name: name
      in: path
      required: true
      schema:
        type: string
      examples:
        Drive:
          value: "Drive:1:1:1"
        Library:
          value: "LS"
        Robot:
          value: "Robot:1"
    limitParam:
      description: The maximum numbers of items to return. If not included, all items are returned.
      in: query
      name: limit
      schema:
        type: integer
        format: int64
        minimum: 1
        example: 10
    mediaType:
      description: Type of media to retrieve.
      name: mediaType
      in: query
      schema:
        $ref: '#/components/schemas/MediaTypes'
      required: false
    offsetParam:
      description: The number of items to skip before starting to collect the result set. If not included, no items are skipped.
      in: query
      name: offset
      schema:
        type: integer
        format: int64
        minimum: 0
        example: 0
    partition:
      description: |-
        Name of the partition. This is returned as `name` from `GET /partitions`.
      name: partition
      in: query
      schema:
        type: string
        example: "Data Partition"
    mediaContainerAddress:
      description: MediaContainer address of inventory to retrieve
      required: true
      name: address
      in: path
      schema:
        $ref: '#/components/schemas/MediaContainerAddress'
    tapName:
      description: Name of TAP to retrieve. This is returned as `name` in the response from `GET /taps`.
      required: true
      name: name
      in: path
      schema:
        $ref: '#/components/schemas/TAPTypes'
    taskID:
      description: |-
        ID of an asynchronous task.
        This is returned as `taskID` from a `GET` request or in the 202 response when starting the task.
      required: true
      name: taskID
      in: path
      schema:
        $ref: '#/components/schemas/TaskID'
    subscriberID:
      description: |-
        ID of a subscriber for library notifications.
        This is returned as `subscriberID` from a `GET` request or in the 201 when adding a subscriber
      required: true
      name: subscriberID
      in: path
      schema:
        $ref: '#/components/schemas/SubscriberID'
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  headers:
    Location:
      description: |-
        URI of the resource
      schema:
        type: string
        format: URI
  responses:
    'default':
      description: An error occurred during the request. See the response for more details.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '202':
      description: |-
        Accepted - Background action in progress
      headers:
        Location:
          description: |-
            URI that can be queried for state
          schema:
            type: string
            format: URI
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AcceptedResponse'
    '204':
      description: |-
        No Content - Action complete
    '400':
      description: |-
        Bad Request - Malformed request.
        If innerError is set, see sense error code for more information
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '401':
      description: |-
        Unauthorized - Login required.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '403':
      description: |-
        Forbidden - Logged in user has insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '404':
      description: |-
        Not Found - Invalid URI.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '409':
      description: |-
        Conflict
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '422':
      description: |-
        Bad Request - Invalid arguments.
        If innerError is set, see sense error code for more information.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '429':
      description: |-
          Too Many Requests - Rate limit exceeded.
      content:
        application/json:
          schema:
              $ref: '#/components/schemas/ErrorResponse'
    '500':
      description: |-
        Permanent Error - See ErrorResponse for details
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '501':
      description: |-
        Not Implemented - See ErrorResponse for details.
        The library does not support the requested action.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    '503':
      description: |-
        Temporary Error - See ErrorResponse for details.
        The library may be starting or in maintenance mode.
        If innerError is set, see sense error code for more information.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
  schemas:
    AcceptedResponse:
      title: AcceptedResponse - Asynchronous Response
      properties:
        taskID:
          $ref: "#/components/schemas/TaskID"
        href:
          description: HTTP reference link to a resource that can be queried for state
          type: string
        message:
          description: If there is no task ID to report, this message will provide details on what action will be performed
          type: string
    AuthSettings:
      title: AuthSettings - Authentication Settings
      description: |-
        Configures valid backend authentication mechanisms.
      required:
        - authenticators
      properties:
        autoLogout:
          type: object
          description: Describes the parameters of the auto-logout feature for any token
          required:
            - refreshTimeout
            - tokenLifetime
          properties:
            refreshTimeout:
              description: Length of time, in seconds, that a token can be refreshed. If set to zero, tokens can be refreshed indefinitely, as long as the current access token is valid.
              type: integer
            tokenLifetime:
              description: Length of time, in seconds, that an access token is valid.
              type: integer
              minimum: 60
        authenticators:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/Authenticator'
      example:
        autoLogout:
          refreshTimeout: 86400
          tokenLifetime: 1200
        authenticators:
          "ldap.mydomain.com":
            type: LDAP
            enabled: true
            readOnlyUser: "ro@library.local"
            readOnlyPwd: PASSWORD
            baseDN: "dc=library,dc=local"
            userNameKey: "sAMAccountName"
            groupsKey: "memberOf"
            trustedCert: false
            port: 389
            superUserGroup: "CN=PowerUsers,OU=Groups,DC=LIBRARY,DC=local"
            adminGroup: "CN=Admins,OU=Groups,DC=LIBRARY,DC=local"
            operatorGroup: "CN=Users,OU=Groups,DC=LIBRARY,DC=local"
            partitionsGroups:
              "Data Partition": "CN=Users,OU=Groups,DC=LIBRARY,DC=local"
          "NATIVE":
            type: NATIVE
            enabled: true
            minimumNumbers: 2
            minimumUpperCase: 2
            minimumLowerCase: 2
            minimumSpecial: 2
            minimumLength: 10
            passwordHistoryLength: 5
            maximumRepeatedCharacters: 3
            passwordExpiration:
              enabled: true
              passwordLifetimeInSeconds: 144000
              expirationWarningSeconds: 14400
              minPasswordAgeInSeconds: 3600
    Authenticator:
      oneOf:
        - $ref: '#/components/schemas/LDAPAuthenticator'
        - $ref: '#/components/schemas/NativeAuthenticator'
      discriminator:
        propertyName: type
        mapping:
          LDAP: '#/components/schemas/LDAPAuthenticator'
          NATIVE: '#/components/schemas/NativeAuthenticator'
    AuthenticatorBase:
      required:
        - enabled
        - type
      properties:
        type:
          type: string
          $ref: '#/components/schemas/AuthenticatorTypes'
        enabled:
          type: boolean
          description: If true, the authentication server is available
    AuthorizationMetadata:
      required:
        - domain
        - username
        - libraryType
        - role
      properties:
        domain:
          type: string
        username:
          type: string
        tokenExpiresAt:
          type: integer
        refreshUntil:
          type: integer
        libraryType:
          $ref: '#/components/schemas/LibraryType'
        passwordExpired:
          type: boolean
        role:
          $ref: '#/components/schemas/GroupNames'
    LibraryActions:
      type: string
      description: |-
        <table>
          <tr>
          <td>POWER_OFF</td>
          <td>Power off the library when possible.</td>
          </tr>
          <tr>
          <td>RESTART</td>
          <td>Power-cycle the library</td>
          </tr>
          <tr>
          <td>BEGIN_DEMO</td>
          <td>WARNING: DO NOT RUN THIS ACTION, as it is used solely for demonstration purposes. This action moves tapes around randomly and does not return them to their original slots.
          If you inadvertently run this action: 1) Run the 'END_DEMO' library action. 2) Run the reset inventory action.</td>
          </tr>
          <tr>
          <td>END_DEMO</td>
          <td>End robotics demonstration mode</td>
          </tr>
        </table>
      enum:
        - "POWER_OFF"
        - "RESTART"
        - "BEGIN_DEMO"
        - "END_DEMO"
    MoveToChambersTest:
      properties:
        values:
          type: array
          items:
            $ref: '#/components/schemas/MoveToChambers'
    MoveToChambers:
      required:
        - location
      properties:
        robotName:
          type: string
          description: |-
            Name of Robot to use (optional). This defaults to both robots when two are detected, and the available robot when either one of the two robots is disabled/unavailable,
            or when there is only one robot. If desired, specify the name of the robot returned by the GET /frus command for type=ROBOT.
        splitCoverage:
          type: boolean
          description: Specifies that the test should split coverage evenly between both robots if two are available. This parameter is ignored if there is only one robot.
        location:
          type: string
          description: |-
            Location of the chamber in the format frame:side:bay:chamber. This is the same location format as returned by GET /magazines.
            With the exception of side, values start at 1 and are specified in decimal. An asterisk can be used to denote every value for a specific location.
            Frame: The frame of a library. Cube libraries only have one frame.
            Side: The side where the chamber is located.
                  In a Cube library, this indicates the left(L) or right(R) side as you are facing the front of the library.
                  In all other Spectra Logic libraries, this indicates the front (f)  or back(b) of the library.
            Bay: The number of the shelving bay containing the chamber. Bays are logical divisions of the library storage chambers.
            Chamber: The number of the chamber in the shelving bay.
                    In a Cube library, chambers within a bay are numbered from back to front, and bottom to top.
                    In all other Spectra Logic libraries, chambers within a bay are numbered from left to right from the perspective of the robot, and from bottom to top.
    MoveTapeToDrivesTest:
      required:
        - tapeBarcode
      properties:
        tapeBarcode:
          type: string
          description: Barcode of the tape to use for the test. Note that the tape must currently be installed in a slot. Can be retrieved from `/inventory`
    MoveToDrive:
      required:
        - driveName
        - robotName
      properties:
        robotName:
          type: string
          description: |-
            Name of robot to use. The name to provide is that returned by the GET /frus command for Type=ROBOT.
        driveName:
          type: string
          description: Name of drive to use. The name to provide is returned by the GET /frus command for Type=DRIVE.
      example:
        robotName: "Robot:1"
        driveName: "Drive:1:3:1"
    MoveToShelfTest:
      required:
        - frameNumber
        - side
        - shelfNumber
      properties:
        frameNumber:
          type: integer
          description: The frame to test
          minimum: 1
          maximum: 255
        side:
          $ref: '#/components/schemas/FrameSide'
        shelfNumber:
          type: integer
          description: The number of the shelf to test, 1 refers to the bottommost shelf
          maximum: 23
          minimum: 1
    FrameSide:
      description: The front or back side of a frame
      type: string
      enum:
        - "FRONT"
        - "BACK"
    LibrarySelfTest:
      required:
        - status
        - startTime
      properties:
        startTime:
          type: string
          format: date-time
          description: Time the self test was started
        endTime:
          type: string
          format: date-time
          description: Time the self test completed
        status:
          type: string
          description: The final status of the self test
        results:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/StatusMessageList'
    LDAPAuthenticator:
      allOf:
        - $ref: '#/components/schemas/AuthenticatorBase'
        - type: object
          required:
            - readOnlyUser
            - baseDN
            - userNameKey
            - groupsKey
            - trustedCert
            - port
            - superUserGroup
          properties:
            readOnlyUser:
              type: string
              description: Username for read-only access to the LDAP server
            readOnlyPwd:
              type: string
              description: Password for read-only access to the LDAP server
            baseDN:
              type: string
              description: Base distinguished name used when searching for users and groups
            userNameKey:
              type: string
              description: LDAP attribute name used for usernames
            groupsKey:
              type: string
              description: LDAP attribute name used for groups
            trustedCert:
              type: boolean
              description: If true, the LDAP server's certificate must be signed by a trusted authority
            port:
              type: integer
              description: Port number used by the LDAP server
              minimum: 1
              maximum: 65535
            superUserGroup:
              type: string
              description: Users in this group have superuser permissions
            adminGroup:
              type: string
              description: Users in this group have administrator permissions
            operatorGroup:
              type: string
              description: Users in this group have operator permissions
            partitionsGroups:
              description: |-
                Mapping of partition names to LDAP group names.
                Operators in mapped groups have access to the corresponding partition.
              type: object
              additionalProperties:
                type: string
    NativeAuthenticator:
      allOf:
        - $ref: '#/components/schemas/AuthenticatorBase'
        - type: object
          description: Password complexity requirements. Setting any parameter to 0 disables that parameter.
          required:
            - minimumNumbers
            - minimumUpperCase
            - minimumLowerCase
            - minimumSpecial
            - minimumLength
            - passwordHistoryLength
            - maximumRepeatedCharacters
          properties:
            minimumNumbers:
              type: integer
              description: Minimum number of numeric characters required in a password
              minimum: 0
            minimumUpperCase:
              type: integer
              description: Minimum number of upper case letters required in a password
              minimum: 0
            minimumLowerCase:
              type: integer
              description: Minimum number of lower case letters required in a password
              minimum: 0
            minimumSpecial:
              type: integer
              description: Minimum number of special characters required in a password
              minimum: 0
            minimumLength:
              type: integer
              description: Minimum length required for a password
              minimum: 0
              default: 6
            passwordHistoryLength:
              type: integer
              description: Number of old passwords that cannot be reused (starting with the most recent password)
              minimum: 0
            maximumRepeatedCharacters:
              type: integer
              description: Maximum number of consecutive, identical characters allowed in a password
              minimum: 0
            passwordExpiration:
              $ref: "#/components/schemas/PasswordExpiration"
    AuthenticatorTypes:
      description: Type of the authentication server
      type: string
      enum:
        - "LDAP"
        - "NATIVE"
    PasswordExpiration:
      description: Password reset parameters.  To disable password reset requirements set 'passwordExpiration.enabled' to false.
      type: object
      required:
        - enabled
        - passwordLifetimeInSeconds
        - minPasswordAgeInSeconds
        - expirationWarningSeconds
      properties:
        enabled:
          type: boolean
          description: Enable password expiration
        passwordLifetimeInSeconds:
          type: integer
          description: Length of time, in seconds, that a password is valid for
          minimum: 1
          default: 86400
        minPasswordAgeInSeconds:
          type: integer
          description: Length of time, in seconds, that you must wait before resetting the password
          minimum: 0
        expirationWarningSeconds:
          type: integer
          description: Length of time, in seconds, before password expiration, after which the user will be given a warning message when they log in
          minimum: 0
    Backup:
      title: Backup - MetaData Stored About a Backup
      description: A backup contains the library settings, library keys, and MLM and DLM data (where supported). It can only be used by the library on which it was created. There can be a maximum of 30 manual backups and 30 automatic backups stored at one time.
      allOf:
        - type: object
          required:
            - name
            - backupType
            - dateCreated
          properties:
            name:
              description: Unique name for the backup in the format SerialNumber-TimeStamp
              type: string
              example: "2004D00_2021-01-28T204652Z"
            backupType:
              $ref: "#/components/schemas/BackupTypes"
            description:
              description: "Description of backup"
              type: string
              example: "Before Package-Update: r12.7.04-01"
            dateCreated:
              type: string
              format: date-time
              description: Date and time the backup was created
      example:
        name: "2021-01-29T193230Z.tar.gz"
        description: "manual backup"
        backupType: "MANUAL"
    BackupRequest:
      title: Backup - MetaData Stored About a Backup
      description: Create a new backup using the given description
      required:
        - description
      properties:
        description:
          description: "Description of backup"
          type: string
          example: "Before Package-Update: r12.7.04-01"
    BackupTypes:
      description: >
        Type of backup:
      type: string
      enum:
        - "AUTOMATIC"
        - "MANUAL"
    BackupList:
      title: BackupList - List of Backups
      description: Paginated list of stored backup files.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Backups
          items:
            $ref: '#/components/schemas/Backup'
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
    BackupSettings:
      title: BackupSettings - Backup Settings
      description: |-
        Settings relating to automatic backups
      properties:
        enabled:
          type: boolean
          description: Enable or disable automatic backups
        frequencyInSeconds:
          type: integer
          minimum: 1
          exclusiveMinimum: true
          description: Amount of time (in seconds) between automatic backups
      required:
        - enabled
        - frequencyInSeconds
      example:
        enabled: true
        frequencyInSeconds: 60
    UpdateBackupSettingsRequest:
      title: BackupSettings - Update Backup Settings
      description: |-
        Partial update of settings related to automatic backups
      properties:
        enabled:
          type: boolean
          description: Enable or disable automatic backups
        frequencyInSeconds:
          type: integer
          minimum: 1
          exclusiveMinimum: true
          description: Amount of time (in seconds) between automatic backups
      example:
        enabled: true
        frequencyInSeconds: 86400
    BasicSettings:
      title: BasicSettings - Library Identification Settings
      description: |-
        User-configurable library settings
      required:
        - name
        - location
        - contact
        - timeMode
        - frontPanelTimezone
      properties:
        name:
          description: |-
            Library name.
          type: string
          example: "Cube"
        contact:
          description: |-
            Contact information for library administrator.
          type: string
        location:
          description: |-
            Physical Location of the library.
          type: string
        timeMode:
          $ref: "#/components/schemas/TimeMode"
        manualTime:
          description: |-
            Deprecated - Use the string variant of timeSource instead. Time to set the library to when changing to 'manual' timeMode, specified in RFC 3339 format
          deprecated: true
          type: string
          format: date-time
        ntpServers:
          description: |-
            Deprecated - Use the 'array of strings' variant of timeSource instead. List of NTP servers to use for time synchronization when using 'NTP' timeMode. The servers may be hostnames
            or IP addresses. The underlying service implements SNTP only and will attempt to synchronize with the
            servers in the order they are listed and will use the first server that responds.
          deprecated: true
          type: array
          items:
            type: string
          minItems: 1
          example:
            - "time.google.com"
            - "time1.google.com"
            - "time2.google.com"
            - "time3.google.com"
        timeSource:
          $ref: "#/components/schemas/LibraryTimeSource"
        frontPanelTimezone:
          description: |-
            Timezone of the library front panel as an IANA Timezone Identifier. The LumOS API always communicates in UTC,
            but the front panel will convert those times to the timezone stored in this setting.
            The front panel interface may restart after changing this setting.
          type: string
          default: "UTC"
          example: "America/Denver"
    BasicSettingsResponse:
      title: BasicSettings - Library Identification Settings
      description: |-
        User-configurable library settings
      required:
        - name
        - location
        - contact
        - timeMode
        - frontPanelTimezone
        - timeSource
      properties:
        name:
          description: |-
            Library name.
          type: string
          example: "Cube"
        contact:
          description: |-
            Contact information for library administrator.
          type: string
        location:
          description: |-
            Physical Location of the library.
          type: string
        timeMode:
          $ref: "#/components/schemas/TimeMode"
        manualTime:
          description: |-
            Deprecated - Use the string variant of timeSource instead. Time to set the library to when changing to 'manual' timeMode, specified in RFC 3339 format
          deprecated: true
          type: string
          format: date-time
        ntpServers:
          description: |-
            Deprecated - Use the 'array of strings' variant of timeSource instead. List of NTP servers to use for time synchronization when using 'NTP' timeMode. The servers may be hostnames
            or IP addresses. The underlying service implements SNTP only and will attempt to synchronize with the
            servers in the order they are listed and will use the first server that responds.
          deprecated: true
          type: array
          items:
            type: string
          minItems: 1
          example:
            - "time.google.com"
            - "time1.google.com"
            - "time2.google.com"
            - "time3.google.com"
        timeSource:
          $ref: "#/components/schemas/LibraryTimeSource"
        frontPanelTimezone:
          description: |-
            Timezone of the library front panel as an IANA Timezone Identifier. The LumOS API always communicates in UTC,
            but the front panel will convert those times to the timezone stored in this setting.
            The front panel interface may restart after changing this setting.
          type: string
          default: "UTC"
          example: "America/Denver"
    UpdateBasicSettingsRequest:
      title: BasicSettings - Library Identification Settings
      description: |-
        User-configurable library settings
      properties:
        name:
          description: |-
            Library name.
          type: string
          example: "Cube"
        contact:
          description: |-
            Contact information for library administrator.
          type: string
        location:
          description: |-
            Physical Location of the library.
          type: string
        timeSource:
          $ref: "#/components/schemas/LibraryTimeSource"
        frontPanelTimezone:
          description: |-
            Timezone of the library front panel as an IANA Timezone Identifier. The LumOS API always communicates in UTC,
            but the front panel will convert those times to the timezone stored in this setting.
            The front panel interface may restart after changing this setting.
          type: string
          default: "UTC"
          example: "America/Denver"
    ManualTime:
      description: |-
        Time to set the library to when changing to 'manual' timeMode, specified in RFC 3339 format
      type: string
      format: date-time
    NTPServers:
      description: |-
        List of NTP servers to use for time synchronization when using 'NTP' timeMode. The servers may be hostnames
        or IP addresses. The underlying service implements SNTP only and will attempt to synchronize with the
        servers in the order they are listed and will use the first server that responds.
      type: array
      items:
        type: string
      minItems: 1
      example:
        - "time.google.com"
        - "time1.google.com"
        - "time2.google.com"
        - "time3.google.com"
    LibraryTimeSource:
      description: |-
        The source for the current time of the library
      oneOf:
        - $ref: '#/components/schemas/ManualTime'
        - $ref: '#/components/schemas/NTPServers'
    TimeMode:
      description: |-
        Deprecated - Use LibraryTimeSource instead. Time mode for the library. The library supports 'manual' and 'ntp'.
      type: string
      deprecated: true
      enum:
        - "MANUAL"
        - "NTP"
    GenericFRUStatus:
      description: A generic FRU status
      allOf:
        - $ref: "#/components/schemas/BaseFRUStatus"
      not:
        anyOf:
          - $ref: '#/components/schemas/DriveStatus'
          - $ref: '#/components/schemas/PMMStatus'
          - $ref: '#/components/schemas/PowerSupply5V12VStatus'
          - $ref: '#/components/schemas/PowerSupply12VStatus'
          - $ref: '#/components/schemas/PowerSupply24VStatus'
          - $ref: '#/components/schemas/RobotStatus'
          - $ref: '#/components/schemas/EthernetSwitchStatus'
          - $ref: '#/components/schemas/FMMStatus'
          - $ref: '#/components/schemas/FCMStatus'
          - $ref: '#/components/schemas/RIMStatus'
          - $ref: '#/components/schemas/SCMStatus'
          - $ref: '#/components/schemas/PCMStatus'
          - $ref: '#/components/schemas/CANRepeaterStatus'
    BasicInfo:
      description: A summary of basic library information.  Fields that cannot be determined are set to "?"
      allOf:
        - $ref: '#/components/schemas/LibraryInfo'
        - $ref: '#/components/schemas/BasicSettingsResponse'
        - $ref: '#/components/schemas/ECInfo'
        - type: object
          required:
            - leftEthernetPortMACAddress
          properties:
            ipv4:
              type: string
              description: The current IPv4 address used by the external ethernet card
            ipv6:
              type: string
              description: The current IPv6 address used by the external ethernet card
            leftEthernetPortMACAddress:
              type: string
              description: The MAC address of the left ethernet port on the Library System.
            rightEthernetPortMACAddress:
              type: string
              description: The MAC address of the right ethernet port on the Library System.
    ContainerTypes:
      description: |-
        The category of media container. Possible values are:
        <table>
          <tr>
            <th><b>Type</b></th>
            <th>Description</th>
          </tr>
          <tr>
            <td>SLOT</td>
            <td>A regular slot in a TeraPack magazine</td>
          </tr>
          <tr>
            <td>IE_SLOT</td>
            <td>A slot in a TeraPack magazine that was assigned to an EE chamber</td>
          </tr>
          <tr>
            <td>DRIVE</td>
            <td>A physical drive</td>
          </tr>
          <tr>
            <td>UNKNOWN</td>
            <td>* UNKNOWN is the default value for any value not listed above. Do not use UNKNOWN as a value for requests.</td>
          </tr>
        </table>
      type: string
      enum:
        - "ALL"
        - "DRIVE"
        - "IE_SLOT"
        - "SLOT"
        - "UNKNOWN"
    ContainerStates:
      type: string
      enum:
        - "ACCESSIBLE"
        - "INACCESSIBLE"
        - "DISABLED"
    ChamberInfo:
      title: ChamberInfo - Chamber information.
      description: Chamber information for media supported on the library.
      required:
        - mediaType
        - availableChambers
      properties:
        mediaType:
          description: The media type of the available chamber(s).
          $ref: '#/components/schemas/MediaTypes'
        availableChambers:
          description: The number of available chambers for the media type.
          type: integer
    Drive:
      title: Drive - Drive Information (Logical and Physical)
      description: |-
        Information about a drive.  This includes configurable hardware information.
      required:
        - drivePath
        - location
        - mediaType
        - name
        - exporting
        - generation
        - formFactor
        - connectionType
      properties:
        address:
          description: |-
            SCSI address of the drive.
            An `8-bit` decimal number is added to the first drive offset of the partition.
            For example, if the partition's drive offset is 256, then the first drive would have an `address` of 256 + 0 = 256, the second an `address` of 256 + 1 = 257, etc.
          type: integer
          format: int32
          minimum: 1
          maximum: 65535
        drivePath:
          description: |-
            Location/path of a drive in the format frame:dba:chamber:slot. Each element can also be found as a field in the `location` property. Slot will be omitted for full-height drives.
            Example: A half-height drive in the top slot of the third chamber of the first drive bay assembly of the first frame has a drivePath of `1:1:3:A`.
            A full-height drive in the first chamber of the second drive bay assembly of the third frame has a drivePath of `1:2:3`.
          type: string
        physicalDrive:
          $ref: '#/components/schemas/PhysicalDrive'
        location:
          $ref: '#/components/schemas/Location'
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        partition:
          description: |-
            Partition to which the drive is currently assigned. Not supplied if the
            drive is not in a partition.
          type: string
        name:
          type: string
          description: Name of drive.
          example: "Drive:1:3:1"
        portConfiguration:
          description: Host side port configuration. May be omitted for non-fibre connected drives.
          $ref: '#/components/schemas/DrivePort'
        exporting:
          description: Indicates if the drive is being used as an exporting control path for the library's robotics. May be set to true for LTO-6 or later generation drives.
          type: boolean
        generation:
          $ref: '#/components/schemas/DriveGeneration'
        formFactor:
          $ref: '#/components/schemas/DriveFormFactor'
        connectionType:
          $ref: '#/components/schemas/DriveConnectionType'
      example:
        name: "Drive:1:1:2"
        address: 257
        drivePath: "1:1:2"
        physicalDrive:
          firmware: "HB83"
          patchLevel: "Unavailable"
          product: "ULTRIUM-HH8"
          serialNumber: "1012004E3A"
          vendor: "IBM"
          manufacturerSerialNumber: "0010WT000234"
          wwn: "21120090A5004E3A"
        location:
          frame: 1
          dba: 1
          number: 2
        mediaType: "LTO"
        partition: "Data Partition"
        exporting: true
        generation: "LTO-9"
        formFactor: "FULL_HEIGHT"
        connectionType: "FIBRE_CHANNEL"
    PhysicalDrive:
      title: PhysicalDrive - Drive Information (Hardware)
      description: |-
        Information about drive hardware.  All fields are read-only and read directly from the drive hardware. If no drive is loaded, all fields are set to `"Unavailable"`.
      required:
        - firmware
        - manufacturerSerialNumber
        - patchLevel
        - product
        - serialNumber
        - vendor
        - wwn
      properties:
        firmware:
          description: Firmware running on the drive, for example "K4K1" or "HB83"
          type: string
        manufacturerSerialNumber:
          description: The serial number assigned to the physical drive by the drive manufacturer. This serial number is required for tracking the drive when it is outside of the library.
          type: string
        patchLevel:
          description: Patch version of the firmware running on the drive. If no patch was applied, this is `"Unavailable"`.
          type: string
        product:
          description: Vendor product name
          type: string
        serialNumber:
          description: The location-based identifier for a drive when it is inside the library. If the drive is replaced, the new drive has the same serial number while it is in the same physical location.
          type: string
        vendor:
          description: Vendor of the drive
          type: string
        wwn:
          description: The Fibre Channel world wide name for a drive. The WWN is a location-based identifier and remains the same if the drive is replaced. It is a 16-character hex number, e.g. `21 12 00 90 A5 00 4E 3A`.
          type: string
    DriveStatus:
      title: DriveStatus - Drive Information (Current Status)
      description: |-
        Current status of a drive.
      allOf:
        - $ref: "#/components/schemas/BaseFRUStatus"
        - type: object
          required:
            - twelveVolt
          properties:
            clockSource:
              $ref: "#/components/schemas/DriveClockSource"
            current:
              type: integer
              description: Current draw through the Drive Power Module in milliamps
            displayMessage:
              $ref: "#/components/schemas/DisplayMessage"
            drivePowerOn:
              type: boolean
              description: Indicates if the drive is powered on
            fanCurrent:
              type: integer
              description: Fan current draw in milliamps
            fanDutyCycle:
              type: integer
              description: Duty cycle setting for the fan
              minimum: 0
              maximum: 100
            fanSpeedPercentage:
              type: integer
              description: Percentage of maximum nominal fan speed. This may be above 100%.
              minimum: 0
              maximum: 255
            faults:
              description: A list of faults detected by the Drive Power Module.
              type: array
              items:
                type: string
            fiveVolt:
              description: Voltage level of the 5V rail in millivolts
              type: integer
              format: int32
            pcbRevision:
              type: string
              description: Revision of the Drive Power Module PCB.
            statusLED:
              $ref: "#/components/schemas/LEDModes"
            temperature:
              type: integer
              description: Sled temperature in degrees Celsius
            twelveVolt:
              description: Voltage level of the 12V rail in millivolts
              type: integer
              format: int32
    DriveClockSource:
      title: DriveClockSource
      description: |-
        Source type for drive power module clock.
      type: string
      enum:
        - Internal8MHz
        - External8MHz
        - ClockMultiplier
        - Internal48MHz
    DriveFirmwareStagingInfo:
      title: DriveFirmwareStagingInfo - Drive Firmware Staging Information
      description: |-
        Information about the drive firmware staging status. The fields are a key-value pair where the key is the drive
        name and the value is the status of the drive firmware staging.
      type: object
      additionalProperties:
        $ref: '#/components/schemas/DriveFirmwareStagingItem'
    DriveFirmwareStagingItem:
      title: DriveFirmwareStagingItem - Drive Firmware Update Information
      description: |-
        Information about the firmware staged on a drive and its current status.
      type: object
      required:
        - status
      properties:
        stagedFirmware:
          description: The firmware staged on the drive
          type: string
        status:
          $ref: "#/components/schemas/DriveFirmwareUpdateStatus"
        taskID:
          $ref: "#/components/schemas/TaskID"
    DriveFirmwareCommitInfo:
      title: DriveFirmwareCommitInfo - Drive Firmware Commit Information
      description: |-
        Information about the drive firmware commit status. The fields are a key-value pair where the key is the drive
        name and the value is the status of the drive firmware committing.
      type: object
      additionalProperties:
        $ref: '#/components/schemas/DriveFirmwareCommitItem'
    DriveFirmwareCommitItem:
      title: DriveFirmwareCommitItem - Drive Firmware Commit Information
      description: |-
        Information about the firmware committed on a drive and its current status.
      type: object
      required:
        - status
      properties:
        status:
          $ref: "#/components/schemas/DriveFirmwareUpdateStatus"
        taskID:
          $ref: "#/components/schemas/TaskID"
    DriveFirmwareUpdateStatus:
      description: Status of the last firmware update.
      type: string
      enum:
        - "In Progress"
        - "Succeeded"
        - "Aborted"
        - "Failed"
        - "Idle"
    DrivePort:
      title: Drive port - Host-Side port Configuration
      description: |-
        The Host-Side configuration of a drive port
      required:
        - addressMode
      properties:
        addressMode:
          description: The addressing mode of the port.
          $ref: '#/components/schemas/PortAddressMode'
        loopID:
          description: The loop ID of the port. Required when using 'HARD' addressing mode.
          $ref: '#/components/schemas/PortLoopID'
    DriveGeneration:
      type: string
      description: Generation of a tape drive.
      enum:
        - "LTO-4"
        - "LTO-5"
        - "LTO-6"
        - "LTO-7"
        - "LTO-8"
        - "LTO-9"
        - "LTO-10"
        - "TS1140"
        - "TS1150"
        - "TS1155"
        - "TS1160"
        - "TS1170"
        - "UNKNOWN"
    DriveFormFactor:
      type: string
      description: Form factor of a tape drive.
      enum:
        - "FULL_HEIGHT"
        - "HALF_HEIGHT"
        - "UNKNOWN"
    DriveConnectionType:
      type: string
      description: Connection type of a tape drive.
      enum:
        - "SAS"
        - "FIBRE_CHANNEL"
        - "UNKNOWN"
    ECInfo:
      title: ECInfo - Library EC Information (Hardware)
      description: |-
        Information about library EC information. All fields are read-only and read directly from the hardware
      required:
        - ec
        - topLevelAssemblyEC
        - topLevelAssemblySerialNumber
        - updated
      properties:
        ec:
          type: integer
          description: EC revision
        topLevelAssemblyEC:
          type: integer
          description: Top level assembly EC revision
        topLevelAssemblySerialNumber:
          type: string
          description: Top level assembly serial number
        updated:
          type: string
          description: Date of the last EC revision change
    Error:
      required:
        - message
      properties:
        message:
          description: A human-readable error message generated by the server
          type: string
        innererror:
          $ref: "#/components/schemas/SenseError"
    ErrorWithCode:
      allOf:
        - $ref: "#/components/schemas/Error"
        - type: object
          required:
            - code
          properties:
            code:
              description: HTTP response status code
              type: integer
    ErrorResponse:
      title: ErrorResponse - A Generic Error Response
      description: |-
        All API error responses include this information.

        When possible, `error.innererror` contains a SCSI status code.
        See the SCSI Developers guide for descriptions of SCSI errors.
      externalDocs:
        description: OData JSON v4 format
        url: 'https://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091'
      required:
        - error
      properties:
        error:
          $ref: "#/components/schemas/ErrorWithCode"
    EthernetSwitchStatus:
      title: Ethernet Switch Status
      description: |-
        The status of the Ethernet switch.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - cpuTemperature
            - fanSpeed
            - faults
            - pcbRevision
            - statusLED
          properties:
            statusLED:
              $ref: "#/components/schemas/LEDModes"
            cpuTemperature:
              type: integer
              description: CPU temperature in degrees Celsius.
            fanSpeed:
              type: integer
              description: Percentage of maximum nominal fan speed. This may be above 100%.
              minimum: 0
              maximum: 255
            faults:
              description: A list of faults detected by the Ethernet switch.
              type: array
              items:
                type: string
            pcbRevision:
              type: string
              description: Revision of the ethernet switch PCB.
          example:
            name: "Ethernet"
            status: "OK"
            statusLED: "ON"
            cpuTemperature: 78
            faults: [ "FPGA Fault" ]
            fanSpeed: 90
            pcbRevision: "0"
            type: "NETWORK_SWITCH"
    Event:
      title: Event - A server initiated event.
      oneOf:
        - $ref: "#/components/schemas/EventTopics"
        - $ref: "#/components/schemas/EventLibraryInitializationStatus"
        - $ref: "#/components/schemas/EventFRU"
        - $ref: "#/components/schemas/EventStatusMessage"
        - $ref: "#/components/schemas/EventMediaMove"
        - $ref: "#/components/schemas/EventExportMove"
        - $ref: "#/components/schemas/EventImportMove"
        - $ref: "#/components/schemas/EventPartitionConfiguration"
        - $ref: "#/components/schemas/EventTaskUpdate"
        - $ref: "#/components/schemas/EventDoorUpdate"
        - $ref: "#/components/schemas/EventLibraryStateUpdate"
        - $ref: "#/components/schemas/EventLibraryServiceInterruption"
        - $ref: "#/components/schemas/EventLibraryDiagnosticUpdate"
      discriminator:
        propertyName: event
        mapping:
          "connected": "#/components/schemas/EventTopics"
          "FRU Added": "#/components/schemas/EventFRU"
          "FRU Removed": "#/components/schemas/EventFRU"
          "Library Initialization Status": "#/components/schemas/EventLibraryInitializationStatus"
          "User Message": "#/components/schemas/EventStatusMessage"
          "Media Move Update": "#/components/schemas/EventMediaMove"
          "Export Move Update": "#/components/schemas/EventExportMove"
          "Import Move Update": "#/components/schemas/EventImportMove"
          "Partition Configuration": "#/components/schemas/EventPartitionConfiguration"
          "Task Update": "#/components/schemas/EventTaskUpdate"
          "Door Update": "#/components/schemas/EventDoorUpdate"
          "Library State Update": "#/components/schemas/EventLibraryStateUpdate"
          "Library Service Interruption": "#/components/schemas/EventLibraryServiceInterruption"
          "Library Diagnostic Update": "#/components/schemas/EventLibraryDiagnosticUpdate"
      example:
        - event: connected
          data:
            - name: Library Status Change
              type: string
            - name: FRU Added
              type: Location
            - name: FRU Removed
              type: Location
            - name: User Message
              type: StatusMessage
            - name: Move Update
              type: Move
            - name: Library Initialization Status
              type: string
        - event: Move Update
          data:
            type: Media
            sourceAddress: 202
            destAddress: 4105
            status: Pending
    EventBase:
      required:
        - event
      properties:
        event:
          type: string
          description: Topic for this event
    EventLibraryInitializationStatus:
      title: Event Library Initialization Status
      description: An event with a status of the library's initialization as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/LibraryInitializationStatus"
    EventFRU:
      title: EventFRU
      description: An event with a location and FRUType as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: object
              required:
                - location
                - type
              properties:
                location:
                  $ref: "#/components/schemas/Location"
                type:
                  $ref: "#/components/schemas/FRUTypes"
    EventStatusMessage:
      title: EventStatusMessage - An event with a status message as data
      description: An event with a status message as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/StatusMessage"
    EventMediaMove:
      title: EventMove - An event with a move as data
      description: An event with a media move as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/MediaMove"
    EventImportMove:
      title: EventMove - An event with an import move as data
      description: An event with an import move as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/ImportMove"
    EventExportMove:
      title: EventMove - An event with an export move as data
      description: An event with a move as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/ExportMove"
    EventPartitionConfiguration:
      title: EventPartitionConfiguration - An event with a partition configuration change as data.
      description: An event with a partition configuration change as data.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: object
              required:
                - partitionName
                - configurationType
              properties:
                partitionName:
                  type: string
                  description: The name of the partition affected by the configuration change.
                  example: "Partition 1"
                configurationType:
                  $ref: "#/components/schemas/PartitionConfigurationType"
    PartitionConfigurationType:
      title: PartitionConfigurationType - The type of partition configuration change.
      description: The type of partition configuration change.
      type: string
      enum:
        - "CREATE"
        - "UPDATE"
        - "DELETE"
    EventTaskUpdate:
      title: EventTaskUpdate - An event with a task ID, state and type as data.
      description: An event with a task ID, state and type used to indicate a change in the task.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: object
              required:
                - taskID
                - taskState
                - taskType
              properties:
                taskID:
                  $ref: "#/components/schemas/TaskID"
                taskState:
                  $ref: "#/components/schemas/TaskStates"
                taskType:
                  $ref: "#/components/schemas/TaskTypes"
    EventDoorUpdate:
      title: EventDoorUpdate - An event with a LibraryDoorStatus as data.
      description: An event with a library door status to indicate a door has been opened or closed.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/LibraryDoorStatus"
    EventLibraryStateUpdate:
      title: EventLibraryStateUpdate - An event with a LibraryState as data.
      description: An event with a library state to indicate a change in the library state.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              $ref: "#/components/schemas/LibraryState"
    EventLibraryServiceInterruption:
      title: EventLibraryServiceInterruption - An event regarding a library service interruption.
      description: An event that indicates an interruption to normal library service. Clients will need to reconnect to the library.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: object
              required:
                - reason
              properties:
                reason:
                  $ref: "#/components/schemas/LibraryServiceInterruptionReason"
    EventTopics:
      title: EventTopics - An event with a collection of event topics as data
      description: An event with a collection of event topics as data
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: array
              items:
                $ref: "#/components/schemas/EventTopic"
    EventTopic:
      title: EventTopic - A Type of Event Available for Subscription
      description:
        A type of event that can be subscribed to
      required:
        - name
        - type
      properties:
        name:
          type: string
          description: Name of this topic
        type:
          type: string
          description: |-
            Schema for the 'data' field returned by this topic.
            Type may be either a custom schema defined in this document, or a basic type.
            This field is omitted if this event has no associated data.
    EventLibraryDiagnosticUpdate:
      title: EventLibraryDiagnosticUpdate - An event with a library diagnostic as data.
      description: An event with a library diagnostic used to indicate a change in the library diagnostic.
      allOf:
        - $ref: "#/components/schemas/EventBase"
        - type: object
          required:
            - data
          properties:
            data:
              type: object
              required:
                - diagnostic
              properties:
                diagnostic:
                  description: The library diagnostic information. Note, some information may be omitted or truncated
                    for brevity.
                  $ref: "#/components/schemas/LibraryDiagnostic"
    LibraryInitializationStatus:
      title: LibraryInitializationStatus - Library Initialization Status
      description: |-
        The status of the library initialization.
      required:
        - status
      properties:
        status:
          type: string
          description: The current status of the library initialization process.
    RIMPort:
      title: RIM Port - Host-Side port Configuration
      description: |-
        The Host-Side configuration of a RIM port
      required:
        - addressMode
        - fibreConnectionMode
      properties:
        addressMode:
          description: The addressing mode of the port.
          $ref: '#/components/schemas/PortAddressMode'
        loopID:
          description: The loop ID of the port. Required when using 'HARD' addressing mode.
          $ref: '#/components/schemas/PortLoopID'
        fibreConnectionMode:
          description: The fibre connection mode.
          $ref: '#/components/schemas/PortConnectionMode'
    PortAddressMode:
      description: Addressing mode for a port.
      type: string
      enum:
        - "HARD"
        - "SOFT"
    PortConnectionMode:
      description: Loop or fabric connection
      type: string
      enum:
        - "LOOP"
        - "FABRIC"
        - "AUTO"
    PortLoopID:
      description: Loop ID for a port.
      type: integer
      minimum: 0
      maximum: 125
    Firmware:
      description: |-
        The firmware version for each component
      required:
        - name
        - version
      properties:
        name:
          description: Firmware name
          type: string
        version:
          description: Firmware version
          type: string
      example:
        name: "BlueScale12.8.03-20200313F"
        version: "12.8.03-20200313F"
    FRU:
      title: FRU - Field Replaceable Unit Static Information
      description: |-
        Generic field replaceable unit information
      oneOf:
        - $ref: '#/components/schemas/GenericFRU'
        - $ref: '#/components/schemas/Robot'
        - $ref: '#/components/schemas/FRUDrive'
        - $ref: '#/components/schemas/RIM'
      discriminator:
        propertyName: type
        mapping:
          POWER_MANAGEMENT_MODULE: '#/components/schemas/GenericFRU'
          POWER_CONTROL_MODULE: '#/components/schemas/GenericFRU'
          EXPORT_CONTROL_MODULE: '#/components/schemas/GenericFRU'
          SERVICE_CONTROL_MODULE: '#/components/schemas/GenericFRU'
          CAN_OVER_POWER: '#/components/schemas/GenericFRU'
          FRAME_MANAGEMENT_MODULE: '#/components/schemas/GenericFRU'
          FRAME_CONTROL_MODULE: '#/components/schemas/GenericFRU'
          LIBRARY_SERVER: '#/components/schemas/GenericFRU'
          POWER_SUPPLY_5V_12V: '#/components/schemas/GenericFRU'
          POWER_SUPPLY_12V: '#/components/schemas/GenericFRU'
          POWER_SUPPLY_24V: '#/components/schemas/GenericFRU'
          NETWORK_SWITCH: '#/components/schemas/GenericFRU'
          ROBOT: '#/components/schemas/Robot'
          DRIVE: '#/components/schemas/FRUDrive'
          CAN_REPEATER: '#/components/schemas/GenericFRU'
          ROBOTICS_INTERFACE_MODULE: '#/components/schemas/RIM'
    GenericFRU:
      title: GenericFRU - A generic FRU controller
      description: A generic field replaceable unit
      allOf:
        - $ref: '#/components/schemas/FRUBase'
      not:
        anyOf:
          - $ref: '#/components/schemas/FRUDrive'
          - $ref: '#/components/schemas/Robot'
          - $ref: '#/components/schemas/RIM'
    FRUBase:
      required:
        - name
        - type
        - fruFirmware
        - actions
      properties:
        name:
          description: name of the FRU
          type: string
        type:
          type: string
          $ref: '#/components/schemas/FRUTypes'
        fruFirmware:
          description: FRU firmware version
          type: string
        actions:
          $ref: '#/components/schemas/FRUActionList'
        manufacturingInfo:
          $ref: '#/components/schemas/ManufacturingInfo'
    FRUActions:
      title: FRUAction - An action that can be performed on a FRU
      description: |-
        <b>Some actions are available on only certain types of Field Replaceable Units.</b>
        <h4>Actions that can be performed on any FRU:</h4>
        <table>
          <tr>
          <td>REPLACE</td>
          <td>mark the unit as ready for replacement.  Equivalent to calling `Disable` and `SetBeacon` followed by `ClearBeacon` and then after replacing the physical unit calling `Enable`.</td>
          </tr>
          <tr>
          <td>SET_BEACON</td>
          <td>Begin to blink the LEDs on the unit to aid in physically locating the FRU</td>
          </tr>
          <tr>
          <td>CLEAR_BEACON</td>
          <td>Return LEDs to automatic mode</td>
          </tr>
          <tr>
          <td>RESET</td>
          <td>Reset the unit. The RESET action for drives is not supported on Cube type libraries, use the RESET_DRIVE instead. </td>
          </tr>
        </table>
        <h4>Actions that can be performed only on a Drive:</h4>
        <table>
          <tr>
          <td>DUMP_DRIVE_TRACE</td>
          <td>"Force a drive dump that can be retrieved using a log gather. This operation removes any existing dump files on the specified drive. If the drive automatically performed a drive dump due to an error condition, forcing a new drive dump deletes the automatic drive dump and useful information may be lost. Only force a drive dump under direction of Spectra Logic Technical Support."</td>
          </tr>
          <tr>
          <td>EJECT_FROM_DRIVE</td>
          <td>Issues an eject command to the drive</td>
          </tr>
          <tr>
          <td>POWER_ON</td>
          <td>Issues a power on command to the drive. This will not re-enable ports for a drive that is included in a partition. To re-enable the ports, send a RESET action to the drive.</td>
          </tr>
          <tr>
          <td>POWER_OFF</td>
          <td>Issues a power off command to the drive. If the drive is in a partition, this action will disable its ports.</td>
          </tr>
          <tr>
          <td>RESET_DRIVE</td>
          <td>Issues a reset command to the drive. This will only reset the tape drive, not the drive controller.
          </tr>
        </table>
        <h4>Actions that can be performed only on a Robot:</h4>
        <table>
          <tr>
          <td>BEGIN_SERVICE</td>
          <td>
            Move the robot near the library door. While the robot is in service, any action requiring the
            robot will return an error. This includes moves as well as action such as POSITIONING_TEST and
            COLUMN_CALIBRATION_TEST. The robot remains powered such that an END_SERVICE action is possible.
          </td>
          </tr>
          <tr>
          <td>END_SERVICE</td>
          <td>Resume normal robot operations.</td>
          </tr>
          <tr>
          <td>POSITIONING_TEST</td>
          <td>Diagnostic robot positioning</td>
          </tr>
          <tr>
          <td>COLUMN_CALIBRATION_TEST</td>
          <td>Diagnostic column calibration issues</td>
          </tr>
          <tr>
          <td>HPT_SELF_TEST</td>
          <td>Self test for High Performance Transporter</td>
          </tr>
        </table>
        <h4>Actions that can be performed only on a SCM:</h4>
        <table>
          <tr>
          <td>LOCK_SERVICE_DOOR</td>
          <td> Prevent the service door from being moved. </td>
          </tr>
          <tr>
          <td>UNLOCK_SERVICE_DOOR</td>
          <td> Allow the service door to be moved. </td>
          </tr>
        </table>
        <h4>Actions that can be performed only on a RIM:</h4>
        <table>
          <tr>
          <td>WRITE_LOGS_TO_USB</td>
          <td> Write the RIM log files to a USB device connected directly to the RIM. The device must be connected prior to running this command. Only FAT-formatted devices are recognized.</td>
          </tr>
        </table>
      type: string
      enum:
        - "BEGIN_SERVICE"
        - "CLEAR_BEACON"
        - "EJECT_FROM_DRIVE"
        - "DUMP_DRIVE_TRACE"
        - "END_SERVICE"
        - "REPLACE"
        - "RESET"
        - "SET_BEACON"
        - "POSITIONING_TEST"
        - "COLUMN_CALIBRATION_TEST"
        - "LOCK_SERVICE_DOOR"
        - "UNLOCK_SERVICE_DOOR"
        - "HPT_SELF_TEST"
        - "WRITE_LOGS_TO_USB"
        - "POWER_ON"
        - "POWER_OFF"
        - "RESET_DRIVE"
    FRUActionList:
      title: FRUActionList - List of Actions available for a field replaceable unit
      description: |-
        List of FRU actions
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of FRU Action
          items:
            $ref: '#/components/schemas/FRUActions'
    FRUList:
      title: FRUList - List of Field Replaceable Units
      description: |-
        List of Field Replaceable Units
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Field Replaceable Units
          items:
            $ref: '#/components/schemas/FRU'
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
    FRUDrive:
      title: FRUDrive - Drive info (Physical and Logical)
      allOf:
        - $ref: '#/components/schemas/FRUBase'
        - type: object
          required:
            - drive
          properties:
            drive:
              $ref: '#/components/schemas/Drive'
      not:
        anyOf:
          - $ref: '#/components/schemas/GenericFRU'
          - $ref: '#/components/schemas/Robot'
          - $ref: '#/components/schemas/RIM'
    ReadElementStatusInformation:
      description: |-
        <b>Information to be included in the response to Read Element Status (RES) commands from the host.</b>
        <table>
          <tr>
          <td>STANDARD</td>
          <td>Standard element descriptors will be returned in Read Element Status (RES) responses. </td>
          </tr>
          <tr>
          <td>TAPE_GENERATION</td>
          <td>Include media domain, media type, drive domain, and drive type in Read Element Status (RES) responses.</td>
          </tr>
          <tr>
          <td>MEDIA_ZONING</td>
          <td>Include zone information and TeraPack barcodes in Read Element Status (RES) responses. Only available when the library is configured with a single partition exported by RIMs. Media Zoning is not supported on Python libraries and must be disabled when configuring a partition.</td>
          </tr>
        </table>
      type: string
      enum:
        - "STANDARD"
        - "TAPE_GENERATION"
        - "MEDIA_ZONING"
    RIM:
      title: Physical information of a Robotics Interface Module (RIM).
      allOf:
        - $ref: '#/components/schemas/FRUBase'
        - type: object
          properties:
            portA:
              description: Current configuration of port A. The port is omitted if it is not configured.
              $ref: '#/components/schemas/RIMPort'
            portB:
              description: Current configuration of port B. The port is omitted if it is not configured.
              $ref: '#/components/schemas/RIMPort'
            wwn:
              description: World Wide Name of the RIM
              type: string
              example: "201F0090A5001EB2"
      not:
        anyOf:
          - $ref: '#/components/schemas/GenericFRU'
          - $ref: '#/components/schemas/Robot'
    StartupScanSettings:
      title: Startup Scan Settings
      type: object
      required:
        - scanMode
      properties:
        scanMode:
          $ref: '#/components/schemas/StartupScanMode'
    StartupScanMode:
      description: |-
        The mode motion will use for startup scans. The library supports 'FULL', 'QUICK', and 'NONE'. 'FULL' will fully scan all library inventory.
        'QUICK' will verify magazine barcodes and report any discrepancies with the known magazine inventory. 'NONE' will not perform a startup scan.
      type: string
      enum:
        - "FULL"
        - "QUICK"
        - "NONE"
    SyslogSettings:
      title: Syslog Settings
      type: object
      required:
        - remoteServer
      properties:
        remoteServer:
          type: string
          description: The IP address or hostname of the remote syslog server. Connections to the server are made over
            UDP and the default port is 514. Remote servers are not validated for reachability.
    FRUStatus:
      title: FRUStatus - Field Replaceable Unit Dynamic Information
      description: |-
        Current status and environment details of a FRU.
      oneOf:
        - $ref: '#/components/schemas/DriveStatus'
        - $ref: '#/components/schemas/GenericFRUStatus'
        - $ref: '#/components/schemas/PMMStatus'
        - $ref: '#/components/schemas/PowerSupply5V12VStatus'
        - $ref: '#/components/schemas/PowerSupply12VStatus'
        - $ref: '#/components/schemas/PowerSupply24VStatus'
        - $ref: '#/components/schemas/RobotStatus'
        - $ref: '#/components/schemas/EthernetSwitchStatus'
        - $ref: '#/components/schemas/FMMStatus'
        - $ref: '#/components/schemas/FCMStatus'
        - $ref: '#/components/schemas/RIMStatus'
        - $ref: '#/components/schemas/SCMStatus'
        - $ref: '#/components/schemas/PCMStatus'
        - $ref: '#/components/schemas/CANRepeaterStatus'
      discriminator:
        propertyName: type
        mapping:
          POWER_MANAGEMENT_MODULE: '#/components/schemas/PMMStatus'
          ROBOTICS_INTERFACE_MODULE: '#/components/schemas/RIMStatus'
          POWER_SUPPLY_5V_12V: '#/components/schemas/PowerSupply5V12VStatus'
          POWER_SUPPLY_12V: '#/components/schemas/PowerSupply12VStatus'
          POWER_SUPPLY_24V: '#/components/schemas/PowerSupply24VStatus'
          POWER_CONTROL_MODULE: '#/components/schemas/PCMStatus'
          EXPORT_CONTROL_MODULE: '#/components/schemas/GenericFRUStatus'
          SERVICE_CONTROL_MODULE: '#/components/schemas/SCMStatus'
          CAN_OVER_POWER: '#/components/schemas/GenericFRUStatus'
          FRAME_MANAGEMENT_MODULE: '#/components/schemas/FMMStatus'
          FRAME_CONTROL_MODULE: '#/components/schemas/FCMStatus'
          DRIVE: '#/components/schemas/DriveStatus'
          LIBRARY_SERVER: '#/components/schemas/GenericFRUStatus'
          ROBOT: '#/components/schemas/RobotStatus'
          NETWORK_SWITCH: '#/components/schemas/EthernetSwitchStatus'
          CAN_REPEATER: '#/components/schemas/CANRepeaterStatus'
      example:
        name: Drive:1:1:1
        type: DRIVE
        status: OK
        current: 523
        drivePowerOn: true
        fanSpeedPercentage: 100
        faults: [ "EEPROM Fault" ]
        statusLED: On
        pcbRevision: "0"
        twelveVolt: 12212
    BaseFRUStatus:
      title: BaseFRUStatus - Base FRU Status
      description: |-
        Base FRU status information common to all FRUs.
      required:
        - name
        - status
        - type
      properties:
        name:
          description: Identifying name of the FRU. This is returned as `name` in the response from `GET /frus`.
          type: string
        status:
          $ref: '#/components/schemas/FRUStatusValue'
        type:
          type: string
          $ref: '#/components/schemas/FRUTypes'
    FRUTypes:
      description: |-
        Field replaceable unit type
      type: string
      enum:
        - "CAN_OVER_POWER"
        - "DRIVE"
        - "EXPORT_CONTROL_MODULE"
        - "FRAME_CONTROL_MODULE"
        - "FRAME_MANAGEMENT_MODULE"
        - "LIBRARY_SERVER"
        - "NETWORK_SWITCH"
        - "POWER_CONTROL_MODULE"
        - "POWER_SUPPLY_5V_12V"
        - "POWER_SUPPLY_12V"
        - "POWER_SUPPLY_24V"
        - "ROBOT"
        - "SERVICE_CONTROL_MODULE"
        - "POWER_MANAGEMENT_MODULE"
        - "CAN_REPEATER"
        - "ROBOTICS_INTERFACE_MODULE"
    FRUStatusValue:
      description: |-
        All possible statuses of the field replaceable unit.
      type: string
      enum:
        - "OK"
        - "IMPAIRED"
        - "INITIALIZING"
        - "UNKNOWN"
      example: "OK"
    TimeResponse:
      title: TimeResponse - A Response to Get Time
      description: |-
        A response to a get time request.
      required:
        - currentTime
      properties:
        currentTime:
          description: The current time on the library
          type: string
          format: date-time
    InventoryActions:
      title: InventoryActions - Action Performed on the Inventory
      description: InventoryActions - An action to be performed on the inventory
      type: string
      enum: [ "RESET" ]
    BasicMotionTest:
      title: BasicMotionTest - A Basic Motion Test for Python type libraries
      description: |-
        A Basic Motion Test for testing Python type library components
        <h4>Basic Motion Tests</h4>
        <table>
          <tr>
          <td>ALL_BASIC_MOTION</td>
          <td>
            This will run all basic motion test diagnostics. It typically takes 15 minutes to complete, but can take up to
            30 minutes for libraries with multiple frames. Host moves are delayed during each test, but resume between each test.
          </td>
          <td>BARCODE_READER</td>
          <td>
            This diagnostic verifies that the transporter barcode reader is operational. It takes less than a minute to complete.
            Host moves will be delayed until the diagnostic completes.
          </td>
          <td>EXERCISE_TAP</td>
          <td>
            This diagnostic takes less than one minute to complete. This diagnostic confirms that the main TAP(s) are operational.
            Bulk TAPs will not be tested. Host moves are delayed until this diagnostic completes.
          </td>
          <td>HAX_BINDING</td>
          <td>
            This diagnostic takes approximately one minute per frame to complete. This diagnostic confirms that there
            are no areas on the HAX that might bind. Host moves are delayed until this diagnostic completes.
          </td>
          <td>HAX_SENSOR</td>
          <td>
            This diagnostic takes less than one minute to complete. This diagnostic confirms that the robotics HAX
            sensor is operational. Host moves are delayed until this diagnostic completes.
          </td>
          <td>MAX_SENSOR</td>
          <td>
            This diagnostic takes less than one minute to complete. This diagnostic confirms that the robotics MAX
            sensor is operational. Host moves are delayed until this diagnostic completes.
          </td>
          <td>PAX_SENSOR</td>
          <td>
            This diagnostic takes less than a minute to complete. This diagnostic confirms that the robotics PAX sensor
            is operational. Host moves are delayed until this diagnostic completes.
          </td>
          <td>RAX_SENSOR</td>
          <td>
            This diagnostic takes less than a minute to complete. This diagnostic confirms that the robotics RAX sensor
            is operational. Host moves are delayed until this diagnostic completes.
          </td>
          <td>SAX_SENSOR</td>
          <td>
            This diagnostic verifies that the transporter SAX sensor is operational. It takes less than a minute to complete.
            Host moves will be delayed until the diagnostic completes.
          </td>
          </tr>
          <td>SHELF_SENSOR</td>
          <td>
            This diagnostic verifies that the transporter shelf sensors are operational. It takes less than a minute to complete.
            Host moves will be delayed until the diagnostic completes.
          </td>
          <td>SNOUT_SENSOR</td>
          <td>
            This diagnostic verifies that the transporter snout sensor is operational. It takes less than a minute to complete.
            Host moves will be delayed until the diagnostic completes.
          </td>
          <td>TAX_50_50_SENSOR</td>
          <td>
            This diagnostic confirms that the robotics TAX 50/50 sensor is operational. Host moves are delayed until
            this diagnostic completes. This diagnostic takes less than a minute to complete.
          </td>
          <td>TAX_TERAPACK_SENSOR</td>
          <td>
            This diagnostic takes less than two minutes to complete. This diagnostic confirms that the TAX magazine
            sensor is operational. Host moves are delayed until this diagnostic completes.
          </td>
          <td>VAX_COLUMN_ALIGNMENT</td>
          <td>
            This diagnostic takes less than three minutes to complete. This diagnostic confirms that the vertical
            alignment of the robotics assembly is within an acceptable range. Check with Support or the FRU guide that
            directed you to run this test to determine an acceptable value. Host moves are delayed until this diagnostic
            completes.
          </td>
          <td>VAX_SENSOR</td>
          <td>
            This diagnostic takes less than a minute to complete. This diagnostic confirms that the robotics VAX sensor
            is operational. Host moves are delayed until this diagnostic completes.
          </td>
        </table>
      type: string
      enum:
        - "ALL_BASIC_MOTION"
        - "EXERCISE_TAP"
        - "BARCODE_READER"
        - "HAX_BINDING"
        - "HAX_SENSOR"
        - "MAX_SENSOR"
        - "PAX_SENSOR"
        - "RAX_SENSOR"
        - "SAX_SENSOR"
        - "SHELF_SENSOR"
        - "SNOUT_SENSOR"
        - "TAX_50_50_SENSOR"
        - "TAX_TERAPACK_SENSOR"
        - "VAX_COLUMN_ALIGNMENT"
        - "VAX_SENSOR"
    LEDModes:
      description: |-
        Indicates the state of an LED
      type: string
      enum:
        - "BLINK_QUICKLY"
        - "BLINK_SLOWLY"
        - "DEVICE_CONTROLLED"
        - "OFF"
        - "ON"
    LibraryInfo:
      title: LibraryInfo - Basic Library Information (Hardware)
      description: |-
        Information about library hardware. All fields are read-only and read directly from the hardware
      required:
        - type
        - serialNumber
      properties:
        type:
          $ref: '#/components/schemas/LibraryType'
        serialNumber:
          type: string
          description: Serial number of the library
        name:
          type: string
          description: Name of this library
        contact:
          type: string
          description: Who to contact about this library
        location:
          type: string
          description: The location of this library
    LibraryType:
      type: string
      description: Type of library. TFINITYNSB denotes a TFinity with no service bays.
      enum:
        - "CUBE"
        - "TFINITY"
        - "TFINITYNSB"
        - "PYTHON"
        - "UNKNOWN"
    NTPStatus:
      title: NTPStatus - Current NTP Status
      description: |-
        The status of the NTP client on the library
      required:
        - active
      properties:
        active:
          description: Indicates whether the NTP service is active on the library
          type: boolean
        ntpServer:
          description: NTP Server currently used
          type: string
        fallbackNTPServers:
          description: List of alternative NTP Server the library can use
          type: array
          items:
            type: string
    LibraryDoorNames:
      description: Names for library doors
      type: string
      enum:
        - "FRONT DOOR"
        - "BACK DOOR"
        - "LEFT SERVICE DOOR"
        - "LEFT SIDE"
        - "LEFT REAR ACCESS"
        - "LEFT SIDE ACCESS"
        - "RIGHT SERVICE DOOR"
        - "RIGHT SIDE"
        - "RIGHT REAR ACCESS"
        - "RIGHT SIDE ACCESS"
        - "RIGHT BULK"
        - "LEFT BULK"
    LibraryDoorStatuses:
      description: Indicates the status of access doors in the library
      type: string
      enum:
        - "CLOSED"
        - "OPEN"
        - "INDETERMINATE"
        - "UNKNOWN"
    LibraryDoorStatus:
      description: The status of each door in the library
      type: object
      required:
        - name
        - status
      properties:
        name:
          $ref: '#/components/schemas/LibraryDoorNames'
        status:
          $ref: '#/components/schemas/LibraryDoorStatuses'
      example:
        name: "BACK DOOR"
        status: "CLOSED"
    LibraryServiceInterruptionReason:
      title: LibraryServiceInterruptionReason - Reason for a library service interruption.
      description: A reason for the interruption.
      type: string
      enum:
        - "REBOOT"
        - "SHUTDOWN"
        - "RESTORE_FROM_BACKUP"
        - "PACKAGE_UPDATE"
    LibraryStatus:
      title: LibraryStatus - Current Library status (Hardware and Software)
      description: |-
        General status of library hardware and software. All fields are read-only.
      required:
        - currentTime
        - doors
        - ntpStatus
        - state
      properties:
        doors:
          type: array
          items:
            $ref: '#/components/schemas/LibraryDoorStatus'
        currentTime:
          description: The current time set on the library
          type: string
          format: date-time
        ntpStatus:
          $ref: '#/components/schemas/NTPStatus'
        state:
          $ref: '#/components/schemas/LibraryState'
      example:
        doors:
          - name: "FRONT DOOR"
            status: "CLOSED"
        currentTime: "2020-05-15T08:43:53Z"
        ntpStatus:
          active: false
        state: "READY"
    LibraryState:
      title: LibraryState - Library State
      description: |-
        The current state of the library.
        <table>
          <tr>
          <td>INITIALIZING</td>
          <td>The library is in process of initializing. Robotics and SCSI devices can be unavailable while the initialization process completes.</td>
          </tr>
          <tr>
          <td>READY</td>
          <td>All services on the library are initialized and ready to process requests.</td>
          </tr>
          <tr>
          <td>MANUAL_INTERVENTION_REQUIRED</td>
          <td>A failure has occurred that requires intervention and is preventing normal operation. Ensure all doors are closed. If the problem persists, check system messages and gather logs for more information.</td>
          </tr>
        </table>
      type: string
      enum:
        - "INITIALIZING"
        - "READY"
        - "MANUAL_INTERVENTION_REQUIRED"
    LibraryDiagnosticList:
      title: LibraryDiagnosticList - List of Library Diagnostics
      description: |-
        A paginated list of library diagnostics.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Library Diagnostics
          items:
            $ref: '#/components/schemas/LibraryDiagnostic'
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
    LibraryDiagnostic:
      title: LibraryDiagnostic - Library Diagnostic Information
      description: |-
        LibraryDiagnostic includes information about the library diagnostic.
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            diagnosticType:
              $ref: '#/components/schemas/LibraryDiagnosticType'
          required:
            - diagnosticType
    LibraryDiagnosticType:
      title: LibraryDiagnosticType - Library Diagnostic Type
      description: The type of library diagnostic.
      type: string
      enum:
        - "ALL_BASIC_MOTION"
        - "BARCODE_READER"
        - "BULK_TAP"
        - "COLUMN_CALIBRATION"
        - "DELETE_GEOMETRY"
        - "EXERCISE_TAP"
        - "HAX_BINDING"
        - "HAX_SENSOR"
        - "HPT_SELF_TEST"
        - "MAX_SENSOR"
        - "MOVE_TO_ALL_CHAMBERS"
        - "MOVE_TO_CHAMBERS"
        - "MOVE_TO_DRIVES"
        - "MOVE_TO_SHELF"
        - "OBSTRUCTION_SCAN"
        - "PAX_SENSOR"
        - "RAX_SENSOR"
        - "ROBOT_POSITIONING"
        - "SAX_SENSOR"
        - "SECURITY_AUDIT"
        - "SHELF_SENSOR"
        - "SNOUT_SENSOR"
        - "TAX_50_50_SENSOR"
        - "TAX_TERAPACK_SENSOR"
        - "VAX_COLUMN_ALIGNMENT"
        - "VAX_SENSOR"
        - "VERIFY_MAGAZINE_BARCODES"
        - "RESET_GEOMETRY"
        - "MOVE_TAPE_TO_DRIVES"
    License:
      title: License - License Information
      description: |-
        License contains information about the license installed on the library. Licenses are used to enable features in the library.
      properties:
        key:
          $ref: '#/components/schemas/LicenseKey'
        type:
          $ref: '#/components/schemas/LicenseType'
        added:
          type: string
          format: date-time
          description: The date the license was added to the library.
        expiration:
          type: string
          format: date-time
          description: The expiration date of the license.
        features:
          oneOf:
            - $ref: '#/components/schemas/PartitionsLicenseFeatures'
            - $ref: '#/components/schemas/CapacityLicenseFeatures'
            - $ref: '#/components/schemas/SoftwareSupportLicenseFeatures'
            - $ref: '#/components/schemas/EncryptionProLicenseFeatures'
            - $ref: '#/components/schemas/KMIPLicenseFeatures'
          discriminator:
            propertyName: type
            mapping:
              PARTITIONS: '#/components/schemas/PartitionsLicenseFeatures'
              CAPACITY: '#/components/schemas/CapacityLicenseFeatures'
              SOFTWARE_SUPPORT: '#/components/schemas/SoftwareSupportLicenseFeatures'
              ENCRYPTION_PRO: '#/components/schemas/EncryptionProLicenseFeatures'
              KMIP: '#/components/schemas/KMIPLicenseFeatures'
      required:
        - key
        - type
        - added
        - features
    LicenseKey:
      type: string
      description: The license key generated by Spectra Logic using the library's serial number.
      pattern: '^[a-zA-Z0-9]{3} [a-zA-Z0-9]{3} [a-zA-Z0-9]{3} [a-zA-Z0-9]{3} [a-zA-Z0-9]{3}$'
      example: "ABC 123 DEF 456 JKL"
    LicenseType:
      title: LicenseType - License Type
      description: The type of license
      type: string
      enum:
        - "PARTITIONS"
        - "CAPACITY"
        - "SOFTWARE_SUPPORT"
        - "ENCRYPTION_PRO"
        - "KMIP"
    EncryptionAuthorizationPassword:
      description: Password to use for encryption operations.
      type: string
      pattern: '^[a-zA-Z0-9\.@_-]*$'
      format: password
    EncryptionAuthorizationSettings:
      description: Settings for encryption authorization.
      type: object
      properties:
        mode:
          $ref: "#/components/schemas/EncryptionMode"
      required:
        - mode
    EncryptionMode:
      title: BlueScaleEncryptionMode
      description: A mode of BlueScale encryption.
      type: string
      enum:
        - "SINGLE_USER"
        - "MULTI_USER"
    BlueScaleEncryptionMoniker:
      description: A name to identify a BlueScale encryption key.
      type: string
      pattern: '^[a-zA-Z0-9\.@_-]+$'
      minLength: 1
      maxLength: 32
    BlueScaleEncryptionKeyInfo:
      description: Information about a BlueScale encryption key.
      type: object
      properties:
        moniker:
          $ref: '#/components/schemas/BlueScaleEncryptionMoniker'
        created:
          type: string
          format: date-time
          description: The date the key was created.
        partitions:
          type: array
          items:
            type: string
          description: The names of partitions that use this key.
      required:
        - moniker
        - created
        - partitions
    BlueScaleEncryptionKeyPassword:
      description: Password to use for encrypting and decrypting BlueScale encryption keys for exports and imports.
      type: string
      pattern: '^[a-zA-Z0-9\.@_-]+$'
      minLength: 1
    BlueScaleEncryptionSecureInitializationState:
      description: The state of secure initialization.
        <table>
        <tr><th>State</th><th>Description</th></tr>
        <tr><td>DISABLED</td><td>Secure initialization is not enabled and no action is required.</td></tr>
        <tr><td>AUTHORIZATION_REQUIRED</td><td>Secure initialization is enabled and an encryption authorization password must be provided to complete initialization.</td></tr>
        <tr><td>COMPLETE</td><td>Secure initialization is complete and drives in encryption enabled partitions are capable of reading and writing data.</td></tr>
        </table>
      type: string
      enum:
        - "DISABLED"
        - "AUTHORIZATION_REQUIRED"
        - "COMPLETE"
    BlueScaleEncryptionSettings:
      type: object
      properties:
        secureInitialization:
          type: boolean
          description: |-
            Indicates if secure initialization is enabled. When enabled, a successful encryption authorization
            is required on startup before the drives in encryption-enabled partitions will read/write
            successfully.
      required:
        - secureInitialization
    X509DistinguishedName:
      description: Distinguished name data for X.509 certificate signing request or X.509 certificate.
      type: object
      properties:
        commonName:
          type: string
          description: The common name for the certificate.
        country:
          type: string
          description: The country for the certificate.
        state:
          type: string
          description: The state for the certificate.
        locality:
          type: string
          description: The locality for the certificate.
        organization:
          type: string
          description: The organization for the certificate.
        organizationalUnit:
          type: string
          description: The organizational unit for the certificate.
      required:
        - commonName
    KMIPServer:
      description: KMIP server information.
      type: object
      properties:
        id:
          type: string
          description: The unique ID of the KMIP server.
        address:
          type: string
          description: The IP address or hostname of the KMIP server.
        port:
          type: integer
          description: The port of the KMIP server.
          minimum: 1
          maximum: 65535
      required:
        - id
        - address
        - port
    KMIPServerStatus:
      description: The status of the KMIP server.
      type: object
      properties:
        connected:
          type: boolean
          description: Indicates if the library is connected to the KMIP server.
        connectionError:
          type: string
          description: The connection failure message if the library is not connected to the KMIP server.
      required:
        - connected
    PartitionsLicenseFeatures:
      title: PartitionsLicenseFeatures - Features enabled by a PARTITIONS license
      description: |-
        PartitionsLicenseFeatures contains information about the features enabled by a PARTITIONS license.
        Multiple PARTITIONS licenses can be installed on a library.
      type: object
      properties:
        partitions:
          description: Indicates if partitioning is enabled by this license.
          type: boolean
      required:
        - partitions
    CapacityLicenseFeatures:
      title: CapacityLicenseFeatures - Features enabled by a CAPACITY license
      description: |-
        CapacityLicenseFeatures contains information about the features enabled by a CAPACITY license.
        Multiple CAPACITY licenses can be installed on a library.
      type: object
      properties:
        chambers:
          description: The number of chambers available for use by this license.
          type: integer
          minimum: 0
      required:
        - chambers
    SoftwareSupportLicenseFeatures:
      title: SoftwareSupportLicenseFeatures - Features enabled by a SOFTWARE_SUPPORT license
      description: |-
        SoftwareSupportLicenseFeatures contains information about the features enabled by a SOFTWARE_SUPPORT license.
        Only one SOFTWARE_SUPPORT license can be installed on a library and adding a new SOFTWARE_SUPPORT license will replace the existing license.
      type: object
      properties:
        update:
          description: Indicates if package updates are enabled by this license.
          type: boolean
        locale:
          description: The locale enabled by this license.
          type: string
      required:
        - update
    EncryptionProLicenseFeatures:
      title: EncryptionProLicenseFeatures - Features enabled by an ENCRYPTION_PRO license
      description: |-
        EncryptionProLicenseFeatures contains information about the features enabled by an ENCRYPTION_PRO license.
        Only one ENCRYPTION_PRO license can be installed on a library and adding a new ENCRYPTION_PRO license will replace the existing license.
      type: object
      properties:
        enabled:
          description: Indicates if encryption pro is enabled by this license.
          type: boolean
      required:
        - enabled
    KMIPLicenseFeatures:
      title: KMIPLicenseFeatures - Features enabled by a KMIP license
      description: |-
        KMIPLicenseFeatures contains information about the features enabled by a KMIP license.
        Multiple KMIP licenses can be installed on a library.
      type: object
      properties:
        drives:
          description: Number of drives that can be used in KMIP enabled partitions. This feature is additive with other KMIP licenses.
            The total number of drives that can be used in KMIP enabled partitions is the sum of all KMIP licenses installed on the library.
          type: integer
          minimum: 0
      required:
        - drives
    Location:
      title: Location - Physical Location of a FRU in the Library
      description: |-
        The location of a FRU in the library
      properties:
        frame:
          description: The number of the frame in which the FRU is located.  In a single-frame library this is always 0.
          type: integer
          minimum: 0
          maximum: 255
        dba:
          description: The number of the DBA within a frame in which the FRU is located
          type: integer
          minimum: 0
          maximum: 255
        chamber:
          description: The number of the chamber in the DBA in which the FRU is located
          type: integer
          minimum: 0
          maximum: 255
        slot:
          description: The slot of a half height drive in the chamber in the DBA in which the drive is located. A is the top slot, B is the bottom slot.
          type: string
          enum:
            - "A"
            - "B"
    Log:
      title: Log - MetaData about a gathered logset
      description: |-
        Metadata relating to a gathered logset
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/LogInfo'
      example:
        taskID: "44b23ff3-470e-4ee3-adf2-8a4830013707"
        state: "RUNNING"
        class: "BASIC"
        type: "LOG_GATHER"
        updated: "2020-12-05T18:32:12Z"
        percent: 90
        parameters:
          startTime: "2020-12-03T00:00:00Z"
          endTime: "2020-12-03T23:59:59Z"
          logTypes:
            can: [ "app", "canA", "canC" ]
            dip-e: [ "adt", "app" ]
            drive: [ "trace" ]
            loglib: [ "loglib" ]
            lumos: [ "app", "config", "messages", "security", "web" ]
            motion: [ "app", "config" ]
            os: [ "kernel", "system" ]
    LogTypes:
      type: array
      items:
        type: string
    LogInfo:
      title: LogInfo - Metadata about a Log
      properties:
        startTime:
          description: The requested starting time (RFC3339 format) to collect logs files from, using the LCM timezone. For example `2020-05-11T08:00:00Z`.
          type: string
          format: date-time
        endTime:
          description: The requested end time (RFC3339 format) to collect logs files up to, using the LCM timezone. For example `2020-07-07T19:00.00Z`.
          type: string
          format: date-time
        logTypes:
          description: The requested set of log types to collect. A log type corresponds to a component running on the library that produces log messages.
          type: object
          additionalProperties:
            type: array
            items:
              type: string
    LogList:
      title: LogList - List of Logs
      description: |-
        List of gathered logsets.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Logs
          items:
            $ref: '#/components/schemas/Log'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
      example:
        count: 2
        value:
          - taskID: "44b23ff3-470e-4ee3-adf2-8a4830013707"
            state: "SUCCEEDED"
            class: "BASIC"
            type: "LOG_GATHER"
            updated: "2020-12-05T18:32:12Z"
            percent: 100
            parameters:
              startTime: '2020-12-03T00:00:00Z'
              endTime: '2020-12-03T23:59:59Z'
              logTypes:
                can: [ "app", "canA", "canC" ]
                dip-e: [ "adt", "app" ]
                drive: [ "trace" ]
                loglib: [ "loglib" ]
                lumos: [ "app", "config", "messages", "security", "web" ]
                motion: [ "app", "config" ]
                os: [ "kernel", "system" ]
          - taskID: "734630f2-01e6-4d89-8028-a0a6f98d859e"
            state: "SUCCEEDED"
            class: "BASIC"
            type: "LOG_GATHER"
            updated: "2020-12-05T18:32:12Z"
            percent: 100
            parameters:
              startTime: "2020-12-03T00:00:00Z"
              endTime: "2020-12-03T23:59:59Z"
              logTypes:
                can: [ "app", "canA", "canC" ]
                dip-e: [ "adt", "app" ]
                drive: [ "trace" ]
                loglib: [ "loglib" ]
                lumos: [ "app", "config", "messages", "security", "web" ]
                motion: [ "app", "config" ]
                os: [ "kernel", "system" ]
    LoginRequest:
      title: LoginRequest - Authentication Request
      description: |-
        The login authentication request
      required:
        - domain
        - username
        - password
      properties:
        domain:
          description: Authenticator to use
          type: string
        password:
          description: Password associated with the username. Valid characters are [a-z][A-Z][0-9] and @`~!#$%^&*()‐_=+[]{}\|;:ʹʺ,.<>/?-'"
          type: string
          format: password
          maxLength: 72
        username:
          description: Username of account
          type: string
    LoginResponse:
      title: LoginResponse - Authentication Response
      description: |-
        Authentication Response
      required:
        - token
        - passwordHasExpired
      properties:
        token:
          type: string
          description: Bearer token to use with subsequent requests
        refreshUntil:
          description: The UNIX epoch time after which the current token can no longer be refreshed. This is equal to the time the token was issued plus the configured refresh timeout.
          type: integer
          format: int64
        tokenExpiresAt:
          description: The UNIX epoch time after which the bearer token expires. This is equal to the time the token was issued plus the configured token lifetime.
          type: integer
          format: int64
        passwordExpiresAt:
          description: For Native Authentication only. The UNIX epoch time at which the password expires.
          type: integer
          format: int64
        passwordHasExpired:
          description: For Native Authentication only. Indicates that the user password expired. Permitted operations are limited.
          type: boolean
        message:
          description: Free-form text describing any issues that might exist for the user when logging in
          type: string
    Magazine:
      title: Magazine - A TeraPack Magazine
      description: |-
        A TeraPack magazine with an array of slots potentially containing media.
      required:
        - barcode
        - location
        - slots
        - state
      properties:
        barcode:
          description: Barcode of the TeraPack magazine
          type: string
        location:
          description: |-
            Current location of the magazine in the format frame:side:bay:drawer or 'Robot' if the magazine is currently in a robot. Element numbers start at 1.
            Frame: The number of the frame from left to right. On the Cube platform there is only one frame.
            Side: The side where the chamber is located. On the Cube platform, this is represented as left(L) or right(R) from the perspective of looking into the library. On any other platform, it is represented as front(f) or back(b) from the robots perspective.
            Bay: The number of the shelving bay containing the chamber.
            Drawer: The number of the chamber in the shelving bay.
            Example: The 2nd drawer on the left in the 6th bay of the first frame has a `location` of `1:L:6:2`.
          type: string
        state:
          description: Current state of magazine.
          $ref: '#/components/schemas/ContainerStates'
        slots:
          type: array
          description: List of slots
          items:
            $ref: '#/components/schemas/MediaContainer'
      example:
        barcode: "RH8C60X"
        state: "ACCESSIBLE"
        slots:
          - containerType: "SLOT"
            address: 4096
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4097
            mediaBarcode: "369885L6"
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4098
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4099
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4100
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4101
            mediaBarcode: "335331L6"
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4102
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4103
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4104
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4105
            mediaBarcode: "032190L6"
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
        location: "1:f:3:13"
    FreePoolMagazine:
      title: FreePoolMagazine - A TeraPack Magazine assigned to the free pool.
      description: |-
        A TeraPack magazine assigned to the free pool with an array of media barcodes.
      required:
        - barcode
        - media
        - mediaType
      properties:
        barcode:
          description: Barcode of the TeraPack magazine
          type: string
        media:
          type: array
          description: List of media barcodes in the magazine
          items:
            type: string
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
      example:
        barcode: "RH8C60X"
        media:
          - "369885L6"
          - "335331L6"
          - "032190L6"
        mediaType: "LTO"
    FreePoolMagazineList:
      title: FreePoolMagazineList - List of Magazines assigned to the free pool
      description: |-
        A list of TeraPack magazines currently loaded on the library that are assigned to the free pool
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of magazines.
          items:
            $ref: '#/components/schemas/FreePoolMagazine'
    MagazineList:
      title: MagazineList - List of Magazines
      description: |-
        A list of TeraPack magazines currently loaded on the library and allocated to a partition
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of magazines.
          items:
            $ref: '#/components/schemas/Magazine'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
      example:
        count: 2
        value:
          - barcode: N9DC6XX
            state: "ACCESSIBLE"
            slots:
              - containerType: "SLOT"
                address: 4096
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4097
                mediaBarcode: "369885L6"
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4098
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4099
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4100
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4101
                mediaBarcode: "335331L6"
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4102
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4103
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4104
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4105
                mediaBarcode: "032190L6"
                mediaType: "LTO"
                partition: "Partition 1"
                containerState: "ACCESSIBLE"
            location: '1:f:3:13'
          - barcode: N9DC6YY
            state: "ACCESSIBLE"
            slots:
              - containerType: "SLOT"
                address: 4116
                mediaBarcode: "414723L5"
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4117
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4118
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4119
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4120
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4121
                mediaBarcode: "000059L5"
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4122
                mediaBarcode: "518523L5"
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4123
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4124
                mediaBarcode: "503013L5"
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
              - containerType: "SLOT"
                address: 4125
                mediaBarcode: "503512L5"
                mediaType: "LTO"
                partition: "Partition 3"
                containerState: "ACCESSIBLE"
            location: 'robot'
    ManufacturingInfo:
      title: Manufacturing Info
      description: |-
        Identifying details of a hardware component. The 'top level assembly' fields refer to the Field Replaceable Unit (FRU) containing the component.
      required:
        - manufactureDate
        - serialNumber
        - ec
        - topLevelAssemblySerialNumber
        - topLevelAssemblyEC
      properties:
        manufactureDate:
          description: The date the component was manufactured.
          type: string
          format: date
        partNumber:
          description: The part number of the component.
          type: string
        serialNumber:
          description: The serial number of the component.
          type: string
        ec:
          description: The Engineering Change (EC) level of the component.
          type: integer
        bomLevel:
          description: The Bill of Materials (BOM) level of the component.
          type: string
        topLevelAssemblySerialNumber:
          description: The serial number of the top level assembly.
          type: string
        topLevelAssemblyEC:
          description: The EC level of the top level assembly.
          type: integer
        topLevelAssemblyPartNumber:
          description: The part number of the top level assembly.
          type: string
        topLevelAssemblyBOMLevel:
          description: The BOM level of the top level assembly.
          type: string
      example:
        manufactureDate: 2022-08-18
        serialNumber: EEP0405011
        ec: 4
        topLevelAssemblySerialNumber: TAP0405003
        topLevelAssemblyEC: 2
    MediaContainer:
      title: MediaContainer - A Container Capable of Holding Media
      description: |-
        A physical location or device in the library which may contain media.
        The `mediaBarcode` parameter is omitted if the container is currently empty.
      required:
        - address
        - containerType
        - mediaType
        - partition
        - containerState
      properties:
        address:
          $ref: '#/components/schemas/MediaContainerAddress'
        containerType:
          $ref: '#/components/schemas/ContainerTypes'
        mediaBarcode:
          $ref: '#/components/schemas/MediaBarcode'
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        partition:
          description: Partition assigned to the inventory element.
          type: string
        containerState:
          $ref: '#/components/schemas/ContainerStates'
    MediaContainerList:
      title: List of MediaContainers
      description: |-
        A list of media containers available as sources or destinations for moves.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of MediaContainers
          items:
            $ref: '#/components/schemas/MediaContainer'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
      example:
        count: 3
        value:
          - containerType: "SLOT"
            address: 4096
            mediaType: "LTO"
            mediaBarcode: "807572L7"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
          - containerType: "SLOT"
            address: 4097
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "INACCESSIBLE"
          - containerType: "DRIVE"
            address: 258
            mediaType: "LTO"
            partition: "Data Partition"
            containerState: "ACCESSIBLE"
    MediaContainerAddress:
      description: The SCSI address of the inventory element. Note that this address is based on the relevant offset in the partition the container is allocated to; two containers in different partitions may have the same address.
      type: integer
      format: int32
      minimum: 1
      maximum: 65535
    MediaBarcode:
      description: |-
        The barcode of a tape cartridge. The mediaBarcode parameter is omitted if the drive does not contain a tape cartridge.
      type: string
    MediaTypes:
      description: |-
        Type of media cartridge or container
        * `UNKNOWN` - UNKNOWN is the default value for any value not listed above. Do not use UNKNOWN as a value for requests.
      type: string
      enum:
        - "LTO"
        - "LTO_CLEAN"
        - "TS"
        - "TS_CLEAN"
        - "UNKNOWN"
    BarcodeOptions:
      description: The selected tape barcode options for the partition. This cannot be set for a specific partition on Python libraries, and instead must be controlled via /settings/barcode.
      type: object
      required:
        - checksumBehavior
        - truncation
        - length
      properties:
        checksumBehavior:
          $ref: '#/components/schemas/ChecksumBehavior'
        truncation:
          $ref: '#/components/schemas/Truncation'
        length:
          description: The number of tape barcode characters to report.
          type: integer
          minimum: 1
          maximum: 16
          default: 16
    ChecksumBehavior:
      description: |-
        The tape barcode checksum behavior for the partition. CHECKSUMMED is the default behavior on TFinity and Cube libraries. IGNORECHECKSUM is the default behavior on Python libraries.
        # `CHECKSUMMED` - Your labels include a checksum and you want the barcode verified against the checksum when it is read. Verification is not generally required, but adds extra confirmation that the barcode label was read correctly by the barcode reader.
        # `NONCHECKSUMMED` - Your labels do not include a checksum.
        # `IGNORECHECKSUM` - Your labels include a checksum character but you do not want the barcode verified against the checksum when it is read.
      type: string
      enum:
        - "CHECKSUMMED"
        - "NONCHECKSUMMED"
        - "IGNORECHECKSUM"
    Truncation:
      description: |-
        The tape barcode truncation mode for the partition. LEFT is the default mode.
        # `LEFT` - You want the library to report only the right-most x characters in the barcode, where x is defined by the BarcodeOptions.length property. For example, if the barcode is 1234567L2 and you configure the library to report the five right-most characters, the library reports the barcode as 567L2.
        # `RIGHT` - You want the library to report only the left-most x characters in the barcode, where x is defined by the BarcodeOptions.length property. For example, if the barcode is 1234567L2 and you configure the library to report only the five left-most characters, the library reports the barcode as 12345.
      type: string
      enum:
        - "LEFT"
        - "RIGHT"
      default: "LEFT"
    MLMDiscoveryMode:
      description: |-
        Operation that will be used for media life management discovery on newly imported media.
        * `AUTO_DISCOVERY` - Auto Discovery will import media and add MLM information from the cartridge to the Library MLM database
        * `PRESCAN` - Prescan will import media and add MLM information from the cartridge to the Library MLM database. Additionally, it will perform a functionality test and health check on imported media.
        * `PASSIVE` - Passive will not perform any discovery on newly imported media. Media will be added to the Library MLM database following a drive unload.
        * `DISABLED` - No discovery will be performed on newly imported media.
      type: string
      enum:
        - "AUTO_DISCOVERY"
        - "PRESCAN"
        - "PASSIVE"
        - "DISABLED"
    LibraryChamberCapacitySummary:
      title: LibraryChamberCapacitySummary - Chamber Capacity Summary for a Library
      description: |-
        Chamber capacity summary for a library.
      required:
        - occupied
        - licensed
        - empty
      properties:
        occupied:
          description: The total number of chambers that are occupied by TeraPack magazines.
          type: integer
        licensed:
          description: The total number of chambers licensed to the library.
          type: integer
        empty:
          description: The total number of unoccupied chambers in the library.
          type: integer
    MediaMove:
      title: Media Move
      description: |-
        Information and State of a Media Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestMedia'
            barcode:
              type: string
            hostInitiated:
              description: Indicates if the move was initiated by a SCSI host. False when the move was issued by LumOS.
              type: boolean
          required:
            - parameters
            - barcode
            - hostInitiated
      example:
        parameters:
          type: Media
          sourceAddress: 258
          destAddress: 4096
        taskID: "7dbbddd8-ff73-11eb-9a03-0242ac130003"
        updated: '2020-08-09T23:16:16.371869538Z'
        percent: 0
        state: PENDING
        barcode: "ABCDEF"
        hostInitiated: false
    ImportMove:
      title: Import Move
      description: |-
        Information and State of an Import Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestImport'
            barcode:
              type: string
          required:
            - parameters
            - barcode
    ExportMove:
      title: Export Move
      description: |-
        Information and State of an Export Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestExport'
          required:
            - parameters
    CleanMove:
      title: Clean Move
      description: |-
        Information and State of a Clean Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestClean'
            cleaningTapeBarcode:
              description: The barcode of the cleaning tape used for the move.
              type: string
            result:
              $ref: '#/components/schemas/CleanMoveResult'
            isManualClean:
              description: Indicates if the cleaning operation was initiated manually.
              type: boolean
            storagePartition:
              description: The name of the storage partition the drive is associated with.
              type: string
            cleaningPartition:
              description: The name of the cleaning partition the cleaning tape is associated with.
              type: string
          required:
            - parameters
            - cleaningTapeBarcode
            - isManualClean
    CleanMoveResult:
      description: |-
        The result of a clean move operation. This will be defined once the cleaning move completes.
      type: string
      enum:
        - "SUCCESS"
        - "FAILED_MEDIA_EXPIRED"
        - "FAILED_DRIVE_NOT_CLEAN"
        - "FAILED_NON_MLM_MEDIA"
        - "FAILED_UNKNOWN_REASON"
        - "FAILED_MOVE_FAILED"
        - "UNKNOWN"
    PartitionAssignMove:
      title: AssignMove - Information and State of a PartitionAssign Move
      description: |-
        Information and State of a Partition Assign Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestPartitionAssign'
          required:
            - parameters
    FreePoolAssignMove:
      title: FreePoolAssignMove - Information and State of a FreePoolAssign Move
      description: |-
        Information and State of an FreePoolAssign Move
      allOf:
        - $ref: '#/components/schemas/Task'
        - type: object
          properties:
            parameters:
              $ref: '#/components/schemas/MoveRequestFreePoolAssign'
          required:
            - parameters
    MediaMoveList:
      title: MediaMoveList - List of Media Moves
      description: |-
        Lists all media moves that have been requested through the API; does not include moves issued via SCSI.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/MediaMove'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
      example:
        - request:
            type: MEDIA
            sourceAddress: 4096
            destAddress: 257
          taskID: "8c6289ea-ff73-11eb-9a03-0242ac130003"
          updated: '2020-07-02T01:51:23Z'
          percent: 0
          state: ACTIVE
    ImportMoveList:
      title: ImportMoveList - List of Import Moves
      description: |-
        Lists all import moves that have been requested through the API; does not include moves issued via a SCSI host.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of imports in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/ImportMove'
        nextLink:
          type: string
          description: |-
            Link to the next page; omitted if this is the last page.
    ExportMoveList:
      title: ExportMoveList - List of Export Moves
      description: |-
        Lists all export moves that have been requested through the API; does not include moves issued via SCSI.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of exports in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/ExportMove'
        nextLink:
          type: string
          description: |-
            Link to the next page; omitted if this is the last page.
    CleanMoveList:
      title: CleanMoveList - List of Media Moves
      description: |-
        Lists all clean moves that have been initiated by LumOS or requested through the LumOS API; does not include moves issued via SCSI.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/CleanMove'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
    PartitionAssignMoveList:
      title: PartitionAssignMoveList - List of PartitionAssign Moves
      description: |-
        Lists all partition assign moves that have been requested through the API.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/PartitionAssignMove'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
    FreePoolAssignMoveList:
      title: FreePoolAssignMoveList - List of FreePoolAssign Moves
      description: |-
        Lists all free pool assign moves that have been requested through the API.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Moves
          items:
            $ref: '#/components/schemas/FreePoolAssignMove'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page
    MoveRequestBase:
      title: MoveRequestBase - Common Data for all Move Requests
      description: |-
        Fields common to all types of MoveRequest. To request a move, see MoveRequestMedia, MoveRequestImport, and MoveRequestExport.
      properties:
        partition:
          description: Only required on multi-partition libraries.
          type: string
    MoveRequestExport:
      title: MoveRequestExport - Request an Export of TeraPack Magazines
      description: |-
        An incoming request to perform an Export move.
      allOf:
        - $ref: '#/components/schemas/MoveRequestBase'
        - type: object
          required:
            - tap
            - magazines
          properties:
            tap:
              $ref: '#/components/schemas/TAPTypes'
            magazines:
              description: Barcode of the magazines to export
              type: array
              minItems: 1
              items:
                type: string
    MoveRequestImport:
      title: MoveRequestImport - Request an Import of TeraPack magazines
      description: |-
        An incoming request to perform an Import move.
      allOf:
        - $ref: '#/components/schemas/MoveRequestBase'
        - type: object
          required:
            - tap
          properties:
            tap:
              $ref: '#/components/schemas/TAPTypes'
            pool:
              $ref: '#/components/schemas/PoolType'
              default: "STORAGE"
    MoveRequestMedia:
      title: MoveRequestMedia - Request a Media Move
      description: |-
        An incoming request to perform a Media move. Supported moves are slot-to-slot, slot-to-drive, and drive-to-slot.
      allOf:
        - $ref: '#/components/schemas/MoveRequestBase'
        - type: object
          required:
            - sourceAddress
            - destAddress
          properties:
            sourceAddress:
              description: MediaContainer Address from `/inventory`
              type: integer
              format: int32
              minimum: 1
              maximum: 65535
            destAddress:
              description: MediaContainer Address from `/inventory`
              type: integer
              format: int32
              minimum: 1
              maximum: 65535
    MoveRequestClean:
      title: MoveRequestClean - Request a Clean Move
      description: |-
        An incoming request to perform a Clean move.
      type: object
      properties:
        driveManufacturerSerial:
          description: The serial number assigned to the physical drive by the drive manufacturer. This can be found in the /frus response.
          type: string
      required:
        - driveManufacturerSerial
    MoveRequestPartitionAssign:
      title: MoveRequestPartitionAssign - Request an Partition Assignment Move
      description: |-
        An incoming request to perform an Partition Assignment Move
      type: object
      properties:
        barcode:
          description: The barcode of the magazine to move.
          type: string
        destPartition:
          description: The name of the destination partition.
          type: string
        destPool:
          $ref: '#/components/schemas/PoolType'
          description: The destination pool for the magazine.
      required:
        - barcode
        - destPartition
        - destPool
    MoveRequestFreePoolAssign:
      title: MoveRequestFreePoolAssign - Request an FreePoolAssign Move
      description: |-
        An incoming request to perform an FreePoolAssign move.
      type: object
      properties:
        barcode:
          description: The barcode of the magazine to assign to the free pool.
          type: string
      required:
        - barcode
    NetworkAddressModes:
      description: Addressing mode to use
      type: string
      enum:
        - "DHCP"
        - "STATIC"
    NetworkSettings:
      title: Network Settings
      description: |-
        Settings for the externally facing library ethernet port
      required:
        - ipv4
        - ipv6
        - port
        - dnsServers
      properties:
        ipv4:
          $ref: "#/components/schemas/NetworkIPSettings"
        ipv6:
          $ref: "#/components/schemas/NetworkIPSettings"
        port:
          description: Port to bind the external HTTPs server. The port can be set to 443 or any value between 1024 and 65535.
          type: integer
          maximum: 65535
          default: 443
        dnsServers:
          description: |-
            List of user-configured DNS servers for name resolution.
            DNS servers provided by DHCP and compiled-in DNS servers will be used if no DNS servers are provided.
            DHCP and compiled-in DNS servers will not appear in the list.
            Providing a full list of DNS servers will override the default DNS servers provided by DHCP. If less than
            3 DNS servers are provided, the remaining DNS servers will be set to the default DNS servers provided by DHCP.
          type: array
          items:
            description: IPv4 or IPv6 address of the DNS server.
            type: string
          maxItems: 3
      example:
        ipv4:
          mode: "STATIC"
          network: "10.0.0.0/24"
          gateway: "10.0.0.1"
        ipv6:
          mode: "DHCP"
        port: 443
        dnsServers: [ "8.8.8.8", "2001:4860:4860::8888" ]
    UpdateNetworkSettingsRequest:
      title: Network Settings
      description: |-
        Settings for the externally facing library ethernet port
      properties:
        ipv4:
          $ref: "#/components/schemas/NetworkIPSettings"
        ipv6:
          $ref: "#/components/schemas/NetworkIPSettings"
        port:
          description: Port to bind the external HTTPs server. The port can be set to 443 or any value between 1024 and 65535.
          type: integer
          maximum: 65535
          default: 443
        dnsServers:
          description: |-
            List of user-configured DNS servers for name resolution.
            DNS servers provided by DHCP and compiled-in DNS servers will be used if no DNS servers are provided.
            DHCP and compiled-in DNS servers will not appear in the list.
            Providing a full list of DNS servers will override the default DNS servers provided by DHCP. If less than
            3 DNS servers are provided, the remaining DNS servers will be set to the default DNS servers provided by DHCP.
          type: array
          items:
            description: IPv4 or IPv6 address of the DNS server.
            type: string
          maxItems: 3
      example:
        ipv4:
          mode: "STATIC"
          network: "10.0.0.0/24"
          gateway: "10.0.0.1"
        ipv6:
          mode: "DHCP"
        port: 443
        dnsServers: [ "8.8.8.8", "2001:4860:4860::8888" ]
    NetworkIPSettings:
      title: NetworkIPSettings - settings for an IP configuration
      description: |-
        Contains basic settings for an IPv4 or IPv6 static address
      required:
        - mode
      properties:
        mode:
          $ref: "#/components/schemas/NetworkAddressModes"
        network:
          description: IP address and network mask in Classless Inter-Domain Routing (CIDR) notation. Only required if mode is STATIC.
          type: string
        gateway:
          description: Address of the default gateway. May only be provided if mode is STATIC.
          type: string
    RemoteAccessSettings:
      title: Remote Access Settings
      description: |-
        Settings for allowing remote access to the Spectra LS
      required:
        - sshEnabled
      properties:
        sshEnabled:
          description: Whether SSH will be active on the Spectra LS. Disabling SSH will not log out current remote sessions.
          type: boolean
    PowerSettings:
      title: Library Power Settings
      description: Library power settings
      properties:
        autoPowerOn:
          type: boolean
          description: |-
            Whether or not the library will automatically turn on after an unexpected power loss event.
        powerButtonShutdownEnabled:
          type: boolean
          description: |-
            Whether or not the power button is able to shut down the library. Note that the power button is always
            able to turn the library on.
      required:
        - autoPowerOn
        - powerButtonShutdownEnabled
      example:
        autoPowerOn: true
        powerButtonShutdownEnabled: false
    UpdatePowerSettingsRequest:
      title: Library Power Settings Update
      description: Library power settings to update
      properties:
        autoPowerOn:
          type: boolean
          description: |-
            Whether or not the library should automatically turn on after an unexpected power loss event.
        powerButtonShutdownEnabled:
          type: boolean
          description: |-
            Whether or not the power button should be able to shut down the library. Note that the power button is always
            able to turn the library on.
      example:
        autoPowerOn: false
    Package:
      title: Package - Metadata About an Update Package
      required:
        - name
        - version
        - created
        - firmware
      properties:
        name:
          description: The unique name for this package
          type: string
        version:
          description: |-
            Version string for this package in the form `{major}.{minor}.{patch}.{build number}`
          type: string
        created:
          type: string
          format: date-time
        firmware:
          type: array
          items:
            $ref: '#/components/schemas/Firmware'
      example:
        name: "1.1.0-2024-01-29-2357.lotf"
        version: "0.1.0"
        created: '2021-01-04T00:00:00-00:00'
        firmware:
          - name: "loglib"
            version: "0.1.0.32"
          - name: "motion"
            version: "0.1.0.32"
          - name: "pmm"
            version: "1.0.11.1"
          - name: "boo"
            version: "119.17.0.14"
          - name: "ecm"
            version: "119.17.0.14"
          - name: "transporter"
            version: "119.17.0.16"
          - name: "picker"
            version: "119.17.0.23"
          - name: "hax"
            version: "119.17.0.7"
          - name: "vax"
            version: "119.17.0.8"
          - name: "lumos"
            version: "0.1.0.199"
          - name: "dip-e"
            version: "0.1.0.199"
          - name: "can-logger"
            version: "0.1.0.199"
          - name: "accio"
            version: "0.1.0.48"
    PackageList:
      title: PackageList - List of Packages
      description: |-
        A list of packages that have been uploaded to the library, including the currently active package
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Packages.
          items:
            $ref: '#/components/schemas/Package'
        nextLink:
          type: string
          description: |-
            Link to the next page, omitted if this is the last page.
      example:
        count: 2
        value:
          - name: "1.1.0-2024-01-29-2357.lotf"
            created: "2020-08-20T14:35:21Z"
            version: "0.1.0"
            firmware: [ ]
          - name: "1.1.0-2024-01-29-2357.lotf"
            created: "2020-11-30T08:43:53Z"
            version: "0.1.1"
            firmware: [ ]
    PackageState:
      title: PackageState - Current Progress of a Package Update
      description: |-
        Summary and detailed information about a package update. If an update is in progress, this will show the in-progress state. Otherwise, it will show the final status of the last update.
        An update comprises several specific subtasks updating different components of the overall system. Which component updaters are run as part of an update to a particular package depends on which files are actually present in the new package.
      allOf:
        - $ref: '#/components/schemas/Task'
        - $ref: '#/components/schemas/PackageUpdateComponents'
      example:
        taskID: "95314db8-ff73-11eb-9a03-0242ac130003"
        updated: '0001-01-01T00:00:00Z'
        percent: 100
        state: SUCCESSFUL
        components:
          Database Updates:
            taskID: "9b27a884-ff73-11eb-9a03-0242ac130003"
            updated: '0001-01-01T00:00:00Z'
            percent: 100
            state: SUCCESSFUL
    PackageUpdateComponents:
      title: PackageUpdateComponents - Package Update Component States
      required:
        - components
      properties:
        components:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/Task'
    PackageUpdateRequest:
      title: PackageUpdateRequest - A request to begin a Package Update
      required:
        - name
      properties:
        name:
          description: The unique name of the package to update to
          type: string
    Partition:
      title: Partition - Logical Partition Information
      required:
        - id
        - name
        - mediaType
        - storageChambers
        - entryExitChambers
        - drives
        - rims
        - slotAddressOffset
        - eeSlotAddressOffset
        - driveAddressOffset
        - slotIQ
        - softLoad
        - mlmDiscoveryMode
        - quickPostScan
        - barcodeOptions
        - readElementStatusInformation
        - encryption
        - emulation
      properties:
        id:
          type: integer
          description: ID number of this partition
        name:
          type: string
          description: Name of the partition.
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        storageChambers:
          type: integer
          description: Number of chambers in the partition available for storage
        entryExitChambers:
          type: integer
          description: Number of chambers in the partition available for imports and exports
        drives:
          type: array
          items:
            $ref: '#/components/schemas/Drive'
          description: List of drives assigned to the partition
        rims:
          type: array
          items:
            $ref: '#/components/schemas/RIMConfiguration'
          description: List of RIMs assigned to the partition.
        slotAddressOffset:
          type: integer
          description: SCSI address at which slot addresses begin
          minimum: 1
          maximum: 65535
          default: 4096
        eeSlotAddressOffset:
          type: integer
          description: The SCSI address at which entry exit slot addresses begin
          minimum: 1
          maximum: 65535
          default: 16
        driveAddressOffset:
          type: integer
          description: The SCSI address at which drive addresses begin
          minimum: 1
          maximum: 65535
          default: 256
        slotIQ:
          type: boolean
          description: ADVANCED SETTING - SlotIQ optimizes robotics performance by allowing the library to virtualize tape locations and optimize the order of moves in a queue to reduce the amount of robotic movement required for any set of moves.
            The displayed locations of virtualized inventory will not reflect the physical locations of media within a library.
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
        softLoad:
          type: boolean
          description: ADVANCED SETTING - Soft Load improves robotics performance for LTO-5 and later generation drives by enabling the drives to automatically load media.
            The risk of damaged media is increased if softload fails.
        cleaningPartition:
          type: string
          description: The name of the associated cleaning partition. Associating a cleaning partition with a partition enables the library to automatically clean the drives in the partition.
        mlmDiscoveryMode:
          $ref: '#/components/schemas/MLMDiscoveryMode'
        quickPostScan:
          $ref: '#/components/schemas/QuickPostScan'
        readElementStatusInformation:
          description: Information to be included in Read Element Status (RES) responses to the host.
          $ref: '#/components/schemas/ReadElementStatusInformation'
        encryption:
          description: Encryption configuration for the partition.
          $ref: '#/components/schemas/EncryptionConfiguration'
        emulation:
          $ref: '#/components/schemas/EmulationOptions'
    CleaningPartition:
      title: CleaningPartition - Logical Cleaning Partition Information.
      description: |-
        A cleaning partition is a partition that is used to store cleaning media. Cleaning partitions are associated with other partitions to enable automatic cleaning of drives in the associated partitions.
        Cleaning partitions are not required to be associated with any other partitions. A cleaning partition can be associated with multiple partitions.
      required:
        - id
        - name
        - mediaType
        - storageChambers
        - associatedPartitions
        - barcodeOptions
      properties:
        id:
          type: integer
          description: ID number of this partition
        name:
          type: string
          description: Name of the partition.
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        storageChambers:
          type: integer
          description: Number of chambers in the partition for storing cleaning media
        associatedPartitions:
          type: array
          description: List of partitions associated with this cleaning partition
          items:
            type: string
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
    CreatePartitionRequest:
      type: object
      required:
        - name
        - mediaType
        - storageChambers
      properties:
        name:
          description: Partition name. This must be unique across all partitions and match the defined pattern. The partition name can not be changed after creation.
          type: string
          pattern: '^[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*$'
          minLength: 1
          maxLength: 32
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        storageChambers:
          type: integer
          minimum: 1
          description: Number of chambers in the partition for storage. This must not exceed the number of available chambers remaining in the library. The number of available chambers in the library is available from GET /chambers.
        entryExitChambers:
          type: integer
          minimum: 0
          default: 0
          description: Number of chambers in the partition available for imports and exports. This must not exceed the number of available chambers remaining in the library. The number of available chambers in the library is available from GET /chambers.
        drives:
          description: List of drives to be in the partition. A drive must be physically present, unassigned to a partition and compatible with the partition media type.
          type: array
          items:
            $ref: '#/components/schemas/DriveConfiguration'
        rims:
          description: List of Robotics Interface Modules (RIMs) to assign to the partition. The assigned RIMs must be physically present. When RIMs are assigned to a partition, drives may not be used as exporting controllers.
          type: array
          items:
            $ref: '#/components/schemas/RIMConfiguration'
        softLoad:
          type: boolean
          description: |
            Soft Load improves robotics performance for LTO-5 and later generation drives.
            Soft Load is not supported on Python libraries and must be disabled.
        slotIQ:
          type: boolean
          description: |
            SlotIQ optimizes robotics performance by allowing the library to virtualize tape locations and optimize the order of moves in a queue to reduce the amount of robotic movement required for any set of moves.
            The displayed locations of virtualized inventory will not reflect the physical locations of media within a library.
            SlotIQ is not supported on Python libraries and must be disabled.
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
        mlmDiscoveryMode:
          $ref: '#/components/schemas/MLMDiscoveryMode'
        cleaningPartition:
          description: The name of the cleaning partition to be associated with this storage partition. This must be a valid cleaning partition name.
          type: string
          example: "Cleaning Partition 1"
        readElementStatusInformation:
          description: Specify information to be included in Read Element Status (RES) responses to the host.
          $ref: '#/components/schemas/ReadElementStatusInformation'
        quickPostScan:
          $ref: '#/components/schemas/QuickPostScan'
        encryption:
          description: Encryption configuration for the partition.
          $ref: '#/components/schemas/EncryptionConfiguration'
        emulation:
          $ref: '#/components/schemas/EmulationOptions'
    DriveConfiguration:
      type: object
      required:
        - name
      properties:
        name:
          description: The name of the drive. This corresponds to the name field of FRUBase which can be retrieved from GET /frus?type=DRIVE.
          type: string
          example: "Drive:1:1:1"
        exporting:
          description: Indicate if the drive will be used as an exporting control path for the library's robotics. May be set to true for LTO-6 or later generation drives.
          type: boolean
    EncryptionConfiguration:
      description: Configuration of the encryption for a partition. No configuration indicates that encryption is disabled.
      type: object
      properties:
        configuration:
          description: Optional configuration for encryption. If not specified, encryption will be disabled.
          oneOf:
            - $ref: '#/components/schemas/BlueScaleEncryptionConfiguration'
            - $ref: '#/components/schemas/KMIPEncryptionConfiguration'
    BlueScaleEncryptionConfiguration:
      type: object
      properties:
        primaryMoniker:
          description: Moniker to be used for drive-based encryption and decryption.
          $ref: '#/components/schemas/BlueScaleEncryptionMoniker'
        decryptionOnlyMonikers:
          description: List of monikers to be used for decryption only. This list must not include the primary moniker.
          type: array
          items:
            $ref: '#/components/schemas/BlueScaleEncryptionMoniker'
          maxItems: 8
      required:
        - primaryMoniker
    KMIPEncryptionConfiguration:
      type: object
      properties:
        reuseKeys:
          description: Reuse keys when tapes are overwritten.
          type: boolean
      required:
        - reuseKeys
    RIMConfiguration:
      type: object
      description: Configuration of a Robotics Interface Module (RIM). At least one port must be configured in order to export the associated partition. Both ports may be configured to provide redundancy.
      required:
        - name
      properties:
        name:
          description: The name of the RIM. This corresponds to the name field of FRUBase which can be retrieved from GET /frus?type=ROBOTICS_INTERFACE_MODULE.
          type: string
          example: "RIM:1:2"
        wwn:
          description: The World Wide Name (WWN) of the RIM.
          type: string
          example: "201F0090A5001EB2"
        portA:
          description: The fibre configuration of port A. Note, changes to this configuration will affect all partitions exported by port A.
          $ref: '#/components/schemas/RIMPort'
        portB:
          description: The fibre configuration of port B. Note, changes to this configuration will affect all partitions exported by port B.
          $ref: '#/components/schemas/RIMPort'
    QuickPostScan:
      type: object
      description: |-
        QuickPostScan will check each cartridge in the partition for media errors that can impact the ability to restore the data. A tape will be queued for QuickPostScan
        when one of the conditions are met. The QuickPostScan operation will be performed on the tape when LumOS receives an InterimMoveRequest following a drive unload.
      required:
        - afterTime
        - afterRead
        - afterWrite
      properties:
        afterTime:
          type: boolean
          description: When enabled, a tape will be queued for QuickPostScan after the specified number of seconds have passed since the last QuickPostScan operation for the tape.
        afterRead:
          type: boolean
          description: When enabled, a tape will be queued for QuickPostScan after it has been read.
        afterWrite:
          type: boolean
          description: When enabled, a tape will be queued for QuickPostScan after it has been written to.
        interval:
          type: integer
          description: When afterTime mode is enabled, this field specifies the amount of seconds between QuickPostScan operations for a tape.
    QuickPostScanQueue:
      type: object
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
        value:
          type: array
          description: List of QuickPostScanItems
          items:
            $ref: '#/components/schemas/QuickPostScanItem'
      description: |-
        QuickPostScanQueue contains the list of tapes that are queued for QuickPostScan. The list is in ascending order based on the time the tape was queued for QuickPostScan.
    QuickPostScanItem:
      type: object
      description: |-
        QuickPostScanItem is an entry in the QuickPostScanQueue.
      required:
        - tapeSerialNumber
        - tapeBarcode
        - queuedTime
        - reason
        - partition
      properties:
        tapeSerialNumber:
          type: string
          description: The serial number of the tape.
        tapeBarcode:
          type: string
          description: The barcode of the tape.
        queuedTime:
          type: string
          format: date-time
          description: The time the tape was queued for QuickPostScan.
        reason:
          $ref: '#/components/schemas/QuickPostScanReason'
        partition:
          type: string
          description: The partition the tape is in.
    QuickPostScanReason:
      type: string
      description: |-
        QuickPostScanReason specifies the reason a tape was queued for QuickPostScan.
      enum:
        - "AFTER_READ"
        - "AFTER_WRITE"
        - "AFTER_TIME"
    CreateCleaningPartitionRequest:
      description: Cleaning partition to be associated with a storage partition. Associating a cleaning partition allows for automatic cleaning of drives in the storage partition.
      type: object
      required:
        - name
        - mediaType
        - storageChambers
      properties:
        name:
          description: Partition name. This must be unique across all partitions and match the defined pattern. The partition name can not be changed after creation.
          type: string
          pattern: '^[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*$'
          minLength: 1
          maxLength: 32
        mediaType:
          $ref: '#/components/schemas/MediaTypes'
        storageChambers:
          type: integer
          minimum: 1
          description: Number of chambers in the partition for storage. This must not exceed the number of available chambers remaining in the library. The number of available chambers in the library is available from GET /chambers.
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
    UpdatePartitionRequest:
      properties:
        storageChambers:
          type: integer
          minimum: 1
          description: Number of chambers in the partition for storage. This must not exceed the number of available chambers remaining in the library.
        entryExitChambers:
          type: integer
          minimum: 0
          default: 0
          description: Number of chambers in the partition available for imports and exports. This must not exceed the number of available chambers remaining in the library.
        drives:
          description: List of drives to be in the partition. A drive must be physically present, unassigned to a partition and compatible with the partition media type.
          type: array
          items:
            $ref: '#/components/schemas/DriveConfiguration'
        rims:
          description: List of Robotics Interface Modules (RIMs) to assign to the partition. The assigned RIMs must be physically present. When RIMs are assigned to a partition, drives may not be used as exporting controllers.
          type: array
          items:
            $ref: '#/components/schemas/RIMConfiguration'
        softLoad:
          type: boolean
          description: |
            Soft Load improves robotics performance for LTO-5 and later generation drives.
            Soft Load is not supported on Python libraries and must be disabled.
        slotIQ:
          type: boolean
          description: |
            SlotIQ optimizes robotics performance by allowing the library to virtualize tape locations and optimize the order of moves in a queue to reduce the amount of robotic movement required for any set of moves.
            The displayed locations of virtualized inventory will not reflect the physical locations of media within a library.
            SlotIQ is not supported on Python libraries and must be disabled.
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
        mlmDiscoveryMode:
          $ref: '#/components/schemas/MLMDiscoveryMode'
        cleaningPartition:
          type: string
          description: The name of the cleaning partition to be associated with this storage partition. This must be a valid cleaning partition name. Provide an empty string to remove the cleaning partition association.
          example: "Cleaning Partition 1"
        readElementStatusInformation:
          description: Specify information to be included in Read Element Status (RES) responses to the host.
          $ref: '#/components/schemas/ReadElementStatusInformation'
        quickPostScan:
          $ref: '#/components/schemas/QuickPostScan'
        encryption:
          description: Encryption configuration for the partition.
          $ref: '#/components/schemas/EncryptionConfiguration'
        emulation:
          $ref: '#/components/schemas/EmulationOptions'
    EmulationOptions:
      type: object
      description: ADVANCED SETTING - Emulation options allow you to control the partition's SCSI Inquiry data. Configuring emulation options is not necessary for most installations, and can cause compatibility issues with your software package. Check with your software vendor or Spectra Logic Technical Support before changing these settings.
      properties:
        configuration:
          description: If this property is not provided, default values will be used for the partition's SCSI Inquiry data.
          type: object
          required:
            - vendor
            - product
          properties:
            vendor:
              description: The vendor for emulation.
              type: string
              pattern: '^[ -~]+$'
              maxLength: 8
            product:
              description: The product for emulation.
              type: string
              pattern: '^[ -~]+$'
              maxLength: 16
      example:
        configuration:
          vendor: QUANTUM
          product: P7000
    UpdateCleaningPartitionRequest:
      properties:
        storageChambers:
          type: integer
          minimum: 1
          description: Number of chambers in the partition for storage. This must not exceed the number of available chambers remaining in the library.
        barcodeOptions:
          $ref: '#/components/schemas/BarcodeOptions'
    ElementStateType:
      type: string
      enum:
        - "ACCESSIBLE"
        - "INACCESSIBLE"
    PoolType:
      type: string
      description: Tapes can exist in the storage pool or the entry/exit pool. Their behavior is identical, but some external systems use the entry/exit pool as the expected destination for imports.
      enum:
        - "STORAGE"
        - "ENTRY_EXIT"
    Robot:
      title: Robot
      description: Information about robotic hardware. All fields are read-only and read directly from the hardware.
      allOf:
        - $ref: '#/components/schemas/FRUBase'
        - type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Name of the robot. The left robot is Robot:1 and the right robot is Robot:2. For libraries that only support a single robot, this field will always be Robot:1.
            hax:
              $ref: '#/components/schemas/RobotSubComponent'
            vax:
              $ref: '#/components/schemas/RobotSubComponent'
            transporter:
              $ref: '#/components/schemas/RobotSubComponent'
      not:
        anyOf:
          - $ref: '#/components/schemas/GenericFRU'
          - $ref: '#/components/schemas/RIM'
      example:
        name: "Robot:1"
        type: "ROBOT"
        fruFirmware: "08.08.04.100"
        actions:
          count: 6
          value:
            - "BEGIN_SERVICE"
            - "COLUMN_CALIBRATION_TEST"
            - "END_SERVICE"
            - "HPT_SELF_TEST"
            - "POSITIONING_TEST"
            - "RESET"
        transporter:
          firmware: "03.06.08.0"
          manufacturingInfo:
            manufactureDate: "2019-02-19"
            serialNumber: "2105106"
            ec: 14
            topLevelAssemblySerialNumber: "HP21852055"
            topLevelAssemblyEC: 21
        hax:
          firmware: "08.07.08.0"
          manufacturingInfo:
            manufactureDate: "2018-03-09"
            serialNumber: "S11897"
            ec: 3
            topLevelAssemblySerialNumber: "V3X1807001"
            topLevelAssemblyEC: 8
        vax:
          firmware: "08.07.08.0"
          manufacturingInfo:
            manufactureDate: "2018-03-09"
            serialNumber: "S02188"
            ec: 2
            topLevelAssemblySerialNumber: "V3X1807001"
            topLevelAssemblyEC: 8
    RobotSubComponent:
      description: Information about a sub-component of the Robot
      type: object
      required:
        - firmware
        - manufacturingInfo
      properties:
        firmware:
          type: string
        manufacturingInfo:
          $ref: '#/components/schemas/ManufacturingInfo'
    RobotInService:
      required:
        - serviceBay
      properties:
        serviceBay:
          $ref: "#/components/schemas/ServiceBays"
        tapeInPicker:
          type: boolean
        teraPackInTransporter:
          type: boolean
        tapeInPickerPreviously:
          type: boolean
        teraPackInTransporterPreviously:
          type: boolean
    RobotStatus:
      title: RobotStatus - Current Robot Status (Hardware)
      description: Status of a specific robot in the library.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          properties:
            inService:
              $ref: "#/components/schemas/RobotInService"
      example:
        name: "Robot:1"
        status: "IMPAIRED"
        inService:
          serviceBay: "LEFT"
          tapeInPicker: true
          teraPackInTransporter: true
          tapeInPickerPreviously: false
          teraPackInTransporterPreviously: false
    SenseError:
      title: SenseError - An Error That Can Be Mapped to Standard or Extended SCSI Sense Information
      description: |-
        SCSI Sense Key, ASC and ASCQ codes to indicate an error.
        See the SCSI Developers guide for descriptions of SCSI errors.
      required:
        - message
        - sense
        - asc
        - ascq
      properties:
        message:
          type: string
          description: Error message that accompanies a SCSI sense code
        sense:
          type: integer
          description: SCSI Sense Key (as a decimal value)
          minimum: 0
          maximum: 15
        asc:
          description: SCSI Additional Sense Code byte (as a decimal value)
          type: integer
          minimum: 0
          maximum: 255
        ascq:
          description: SCSI Additional Sense Code Qualifier byte (as a decimal value)
          type: integer
          minimum: 0
          maximum: 255
      example:
        message: "LOGICAL UNIT IS IN PROCESS OF BECOMING READY"
        sense: 2
        asc: 4
        ascq: 1
    ServiceBays:
      type: string
      enum:
        - "LEFT"
        - "RIGHT"
    StatusMessageList:
      title: StatusMessage - List of Status Messages
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          description: List of Status Messages
          items:
            $ref: '#/components/schemas/StatusMessage'
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
      example:
        count: 4
        value:
          - created: '2021-01-27T21:51:43Z'
            id: Motion_58_MOTION_MSG_HAX_BLOCKED_INITIALIZATION
            severity: FATAL_ERROR
            source: Motion
            message: >-
              The HAX axis is blocked while initializing the robotics. This
              could mean either the home sensor is not working, the axis has an
              obstruction, or the VAX column is out of alignment. Examine the
              library to determine the cause.
            uid: '1'
            read: false
          - created: '2021-01-27T21:51:43Z'
            id: Motion_38_MOTION_MSG_MSG_FATAL_RESTART_ERROR
            severity: FATAL_ERROR
            source: Motion
            message: >-
              The robot encountered a problem it could not recover from. The
              robotics firmware will now reboot in an attempt to recover from
              this situation. If this situation persists, contact technical
              support.
            uid: '2'
            read: false
          - created: '2021-01-27T21:54:17Z'
            id: Motion_15_MOTION_MSG_TAPE_IN_SNOUT
            severity: FATAL_ERROR
            source: Motion
            message: >-
              Tape is in picker, and cannot be put away Remove side cover and
              remove tape from picker, then cycle library power.
            uid: '3'
            read: false
          - created: '2021-01-27T21:54:17Z'
            id: Motion_38_MOTION_MSG_MSG_FATAL_RESTART_ERROR
            severity: FATAL_ERROR
            source: Motion
            message: >-
              The robot encountered a problem it could not recover from. The
              robotics firmware will now reboot in an attempt to recover from
              this situation. If this situation persists, contact technical
              support.
            uid: '4'
            read: true
    StatusMessage:
      title: StatusMessage - A Generic Library Status Message
      description: |-
        Each library status message contains an id and a severity.
      required:
        - created
        - id
        - severity
        - source
        - message
        - uid
        - read
      properties:
        created:
          description: Date and time that the message was created
          type: string
          format: date-time
        id:
          description: The identifier of the message used by components to identify the message
          type: string
        severity:
          $ref: '#/components/schemas/Severities'
        source:
          description: The name of the hardware or software component that generated the message
          type: string
        message:
          description: A human-readable version of the message that may also be translated according to the configured locale
          type: string
        remedy:
          description: A suggested action to fix an error in the case where `message` describes an error. Omitted otherwise.
          type: string
        uid:
          description: A unique identifier for the message
          type: string
        read:
          description: Indicates if the message has been read or not.
          type: boolean
    Severities:
      type: string
      enum:
        - "ERROR"
        - "FATAL_ERROR"
        - "INFO"
        - "SUMMARY"
        - "WARNING"
    DisplayMessage:
      title: DisplayMessage - Drive Display Message
      description: |-
        The current message on the drive display
      required:
        - value
        - description
      properties:
        value:
          description: Current message displayed on the drive display screen
          type: string
        description:
          description: Additional context for the displayed value, if available
          type: string
    FMMFanStatus:
      title: Frame Management Module Status.
      required:
        - present
        - speed
      properties:
        present:
          description: Indicates if a fan pair is present in the FMM. Note that this flag is shared by pairs of fans -- 1 and 2 are shared, 3 and 4 are shared, etc.
          type: boolean
        speed:
          description: Speed of the fan, in RPM
          type: integer
    FMMStatus:
      title: Frame Management Module Status.
      description: |-
        Current status and environment details of the Frame Management Module (FMM).
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - twentyFourVolt
            - fiveVolt
            - fanRailVolt
            - switchedRailVolt
            - twentyFourCurrent
            - power
            - sampleRate
            - samples
            - fmmTemperature
            - epmTemperature
            - frame2FrameTemperature
            - frame2FrameAttached
            - frame2Frame5VEnabled
            - fansEnabled
            - fanStatus
            - backSwitchOpen
            - filterSwitchOpen
            - frontSwitchOpen
            - safetyInterlockOpen
            - tapFrontDoorSafetyInterlockOpen
            - frameNumber
            - driveFrame
            - hydraLibraryType
            - powerSupply1Fault
            - powerSupply2Fault
            - powerSupply1Present
            - powerSupply2Present
            - switchedRailState
            - robotPowerEnabled
            - internalLEDCtlrsInitialized
            - externalLEDCtlrsInitialized
            - chassisID
            - auxSwitch
            - tapLoopback
            - ebiLoopback
            - epmLoopback
            - leftLoopback
            - rightLoopback
            - scmLoopback
            - semLoopback
            - newLightsExist
            - libCommExists
            - tapConnected
            - serviceFramePowerBoardPresent
            - semPresent
            - epmPresent
            - serviceFramePowerSWRailLoopback
            - fmmDoorOpen
            - leftSidePanelClosed
            - frontPanelClosed
            - rightSidePanelClosed
            - twentyFourVoltEBIEPMGood
            - frameRailPower1
            - frameRailPower2
            - global24vSWRailOn
            - globalGndSWRailOn
            - twentyFourVoltRoboticPowerGood
            - switchedRailPowerGood
            - safetyClosed
            - safetyOverrideSwitch
            - fiveVoltFMMReset
            - fiveVoltSCMReset
            - fmmAuxSensor
            - fmmAuxSensorPresent
            - libCommReset
            - serviceBayDoorClosed
            - led0
            - led1
            - led2
            - led3
            - led4
            - led5
            - twentyFourVoltServiceFramePowerHS1Good
            - twentyFourVoltServiceFramePowerHS2Good
            - lbSafetyFrontExist
            - lbSafetyLeftExist
            - lbSafetyRightExist
          properties:
            twentyFourVolt:
              description: Voltage level of the 24 Volt supply in millivolts
              type: integer
              format: int32
            fiveVolt:
              description: Voltage level of the 5 Volt supply in millivolts
              type: integer
              format: int32
            fanRailVolt:
              description: Voltage level of the fan rail in millivolts
              type: integer
              format: int32
            switchedRailVolt:
              description: Voltage level of the switched rail in millivolts
              type: integer
              format: int32
            twentyFourCurrent:
              description: Current level of the twenty four volt in milliamps
              type: integer
              format: int32
            power:
              description: Power level expressed in watts
              type: integer
              format: int32
            sampleRate:
              description: Seconds between samples of power
              type: integer
              format: int32
            samples:
              description: Number of samples taken
              type: integer
              format: int32
            fmmTemperature:
              description: FMM temperature in degrees Celsius
              type: integer
              format: int32
            epmTemperature:
              description: Expansion Power Module temperature in degrees Celsius
              type: integer
              format: int32
            frame2FrameTemperature:
              description: Frame-to-Frame temperature in degrees Celsius
              type: integer
              format: int32
            frame2FrameAttached:
              description: Indicates if the Frame-to-Frame board is present
              type: boolean
            frame2Frame5VEnabled:
              description: Indicates if the Frame-to-Frame 5 volt supply is enabled
              type: boolean
            fansEnabled:
              description: Indicates if the fans are enabled
              type: boolean
            fanStatus:
              description: Status of the fans installed (10 possible)
              type: object
              additionalProperties:
                $ref: "#/components/schemas/FMMFanStatus"
            backSwitchOpen:
              description: Indicators if the back switch is open
              type: boolean
            filterSwitchOpen:
              description: Indicates if the filter switch is open
              type: boolean
            frontSwitchOpen:
              description: Indicates if the front switch is open
              type: boolean
            safetyInterlockOpen:
              description: Indicates the safety interlock is open
              type: boolean
            tapFrontDoorSafetyInterlockOpen:
              description: Indicates if the TAP front door safety interlock is open
              type: boolean
            frameNumber:
              description: Frame number
              type: integer
              format: int32
            driveFrame:
              description: Drive frame number
              type: integer
              format: int32
            hydraLibraryType:
              description: Indicates if this is a Hydra Library
              type: boolean
            powerSupply1Fault:
              description: Indicates if power supply 1 has a fault
              type: boolean
            powerSupply2Fault:
              description: Indicates if power supply 2 has a fault
              type: boolean
            powerSupply1Present:
              description: Indicates if power supply 1 is present
              type: boolean
            powerSupply2Present:
              description: Indicates if power supply 2 is present
              type: boolean
            switchedRailState:
              description: Current switched rail state
              type: string
              enum: [
                "Neither",
                "TwentyFourVolt",
                "Ground",
              ]
            robotPowerEnabled:
              description: Indicates if robot power is enabled
              type: boolean
            internalLEDCtlrsInitialized:
              description: List of internal controllers that are initialized
              type: array
              items:
                type: integer
            externalLEDCtlrsInitialized:
              description: List of external controllers that are initialized
              type: array
              items:
                type: integer
            chassisID:
              description: Chassis ID
              type: integer
              format: int32
            auxSwitch:
              description: For internal use only
              type: integer
              format: int32
            tapLoopback:
              description: Indicates if the TAP Loopback is enabled
              type: boolean
            ebiLoopback:
              description: Indicates if the EBI Loopback is enabled
              type: boolean
            epmLoopback:
              description: Indicates if the EPM Loopback is enabled
              type: boolean
            leftLoopback:
              description: Indicates if the Left Loopback is enabled
              type: boolean
            rightLoopback:
              description: Indicates if the Right Loopback is enabled
              type: boolean
            scmLoopback:
              description: Indicates if the SCM Loopback is enabled
              type: boolean
            semLoopback:
              description: Indicates if the SEM Loopback is enabled
              type: boolean
            newLightsExist:
              description: Indicates if the new Light board present. BOA libraries use old Light boards while TFinity libraries use new Light boards
              type: boolean
            libCommExists:
              description: LIBCOMM Exists
              type: boolean
            tapConnected:
              description: Indicates if the TAP is connected
              type: boolean
            serviceFramePowerBoardPresent:
              description: Service frame power board present
              type: boolean
            semPresent:
              description: Indicates if the SEM is present
              type: boolean
            epmPresent:
              description: Indicates if the Expansion Power Module is present
              type: boolean
            serviceFramePowerSWRailLoopback:
              description: Service frame power Switch Rail loopback
              type: boolean
            fmmDoorOpen:
              description: Indicates if FMM door is open
              type: boolean
            leftSidePanelClosed:
              description: Indicates if the left side panel is closed
              type: boolean
            frontPanelClosed:
              description: Indicates if the front panel is closed
              type: boolean
            rightSidePanelClosed:
              description: Indicates if the right side panel is closed
              type: boolean
            twentyFourVoltEBIEPMGood:
              description: Indicates if the 24 volt Electronics Bay Interconnect (EBI) Expansion Power Module (EPM) is good
              type: boolean
            frameRailPower1:
              description: Indicates if frame rail power 1 is on
              type: boolean
            frameRailPower2:
              description: Indicates if frame rail power 2 is on
              type: boolean
            global24vSWRailOn:
              description: Indicates if global 24 Volt Switch Rail is on
              type: boolean
            globalGndSWRailOn:
              description: Indicates if global Ground Switch Rail is on
              type: boolean
            twentyFourVoltRoboticPowerGood:
              description: Indicates if the 24 volt Robot power is good
              type: boolean
            switchedRailPowerGood:
              description: Indicates if the Switched Rail power is good
              type: boolean
            safetyClosed:
              description: Indicates if the safety is closed
              type: boolean
            safetyOverrideSwitch:
              description: Indicates if the safety override switch is closed
              type: boolean
            fiveVoltFMMReset:
              description: Five volt FMM has been reset
              type: boolean
            fiveVoltSCMReset:
              description: Five volt SCM has been reset
              type: boolean
            fmmAuxSensor:
              description: FMM aux sensor
              type: boolean
            fmmAuxSensorPresent:
              description: The FMM Aux sensor. Indicates that the sensor is present.
              type: boolean
            libCommReset:
              description: Indicates if the Library communication was reset
              type: boolean
            serviceBayDoorClosed:
              description: Indicates if the service bay door is closed
              type: boolean
            led0:
              description: Indicates if LED0 is lit
              type: boolean
            led1:
              description: Indicates if LED1 is lit
              type: boolean
            led2:
              description: Indicates if LED2 is lit
              type: boolean
            led3:
              description: Indicates if LED3 is lit
              type: boolean
            led4:
              description: Indicates if LED4 is lit
              type: boolean
            led5:
              description: Indicates if LED5 is lit
              type: boolean
            twentyFourVoltServiceFramePowerHS1Good:
              description: Indicates that the +24 volt service frame power hot-swap1(HS1) is good
              type: boolean
            twentyFourVoltServiceFramePowerHS2Good:
              description: Indicates that the +24 volt service frame power hot-swap2(HS2) is good
              type: boolean
            lbSafetyFrontExist:
              description: Indicates if the Loopback Safety front exists
              type: boolean
            lbSafetyLeftExist:
              description: Indicates if the Loopback Safety left exists
              type: boolean
            lbSafetyRightExist:
              description: Indicates if the Loopback Safety right exists
              type: boolean
          example:
            name: FMM
            twentyFourVolt: 23
            fiveVolt: 5
            fanRailVolt: 5
            switchedRailVolt: 10
            twentyFourCurrent: 100
            power: 20
            sampleRate: 10
            samples: 100
            fmmTemperature: 10
            epmTemperature: 20
            frame2FrameTemperature: 25
            frame2FrameAttached: true
            frame2Frame5VEnabled: true
            fansEnabled: true
            fanStatus:
              Fan1:
                present: true
                speed: 30
              Fan2:
                present: true
                speed: 30
              Fan3:
                present: true
                speed: 30
              Fan4:
                present: true
                speed: 30
              Fan5:
                present: true
                speed: 30
              Fan6:
                present: true
                speed: 30
              Fan7:
                present: true
                speed: 30
              Fan8:
                present: true
                speed: 30
              Fan9:
                present: true
                speed: 30
              Fan10:
                present: true
                speed: 30
            backSwitchOpen: false
            filterSwitchOpen: false
            frontSwitchOpen: false
            safetyInterlockOpen: false
            tapFrontDoorSafetyInterlockOpen: true
            frameNumber: 1
            driveFrame: 2
            hydraLibraryType: true
            powerSupply1Fault: false
            powerSupply2Fault: false
            powerSupply1Present: true
            powerSupply2Present: true
            switchedRailState: "TwentyFourVolt"
            robotPowerEnabled: true
            internalLEDCtlrsInitialized: [ 1, 3 ]
            externalLEDCtlrsInitialized: [ 2, 4 ]
            chassisID: 10
            auxSwitch: 1
            tapLoopback: false
            ebiLoopback: false
            epmLoopback: false
            leftLoopback: false
            rightLoopback: false
            scmLoopback: false
            semLoopback: false
            newLightsExist: true
            libCommExists: true
            tapConnected: false
            serviceFramePowerBoardPresent: true
            semPresent: true
            epmPresent: true
            serviceFramePowerSWRailLoopback: true
            fmmDoorOpen: false
            leftSidePanelClosed: true
            frontPanelClosed: true
            rightSidePanelClosed: true
            twentyFourVoltEBIEPMGood: true
            frameRailPower1: true
            frameRailPower2: true
            global24vSWRailOn: true
            globalGndSWRailOn: true
            twentyFourVoltRoboticPowerGood: true
            switchedRailPowerGood: true
            safetyClosed: true
            safetyOverrideSwitch: true
            fiveVoltFMMReset: false
            fiveVoltSCMReset: false
            fmmAuxSensor: true
            fmmAuxSensorPresent: true
            libCommReset: true
            serviceBayDoorClosed: true
            led0: true
            led1: true
            led2: true
            led3: true
            led4: true
            led5: true
            twentyFourVoltServiceFramePowerHS1Good: true
            twentyFourVoltServiceFramePowerHS2Good: true
            lbSafetyFrontExist: true
            lbSafetyLeftExist: true
            lbSafetyRightExist: true
    FCMFanStatus:
      title: Fan and Light Module Summary Status.
      required:
        - powerOn
        - speed
        - speedSetting
      properties:
        powerOn:
          description: Indicates if the fan power is on
          type: boolean
        speed:
          description: Speed of the fan, in RPM
          type: integer
        speedSetting:
          description: The configured fan speed setting
    FCMStatus:
      title: Fan Control Module Status
      description: |-
        Current status and environment details of the fan control module (FCM).
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - temperature
            - backPanelOpen
            - filterPanelOpen
            - fanPanelOpen
            - fanStatus
            - boardVoltage
            - fanInputVoltage
            - fanSpeedVoltage
            - lightBank1On
            - lightBank2On
            - lightBank3On
            - fanSpeedOutput
            - newFanCalibrated
            - newFilterCalibrated
          properties:
            temperature:
              description: FCM Temperature in degrees Celsius
              type: integer
              format: int32
            backPanelOpen:
              description: Indicates if the back panel is open
              type: boolean
            fanPanelOpen:
              description: Indicates if the fan panel is open
              type: boolean
            fanStatus:
              description: Status of the installed fans (10 possible)
              type: object
              additionalProperties:
                $ref: "#/components/schemas/FCMFanStatus"
            filterPanelOpen:
              description: Indicates if the filter panel is open
              type: boolean
            boardVoltage:
              description: Board voltage in millivolts
              type: integer
              format: int32
            fanInputVoltage:
              description: Fan input voltage in millivolts
              type: integer
              format: int32
            fanSpeedVoltage:
              description: Fan speed voltage in millivolts
              type: integer
              format: int32
            lightBank1On:
              description: Indicates if light bank 1 is on
              type: boolean
            lightBank2On:
              description: Indicates if light bank 2 is on
              type: boolean
            lightBank3On:
              description: Indicates if light bank 3 is on
              type: boolean
            fanSpeedOutput:
              description: Fan speed output
              type: integer
              format: int32
            newFanCalibrated:
              description: Indicates if new fan is calibrated
              type: boolean
            newFilterCalibrated:
              description: Indicates if new filter is calibrated
              type: boolean
          example:
            name: FCM
            temperature: 30
            backPanelOpen: false
            fanPanelOpen: false
            fanStatus:
              Fan1:
                powerOn: true
                speed: 70
                speedSetting: 8
              Fan2:
                powerOn: true
                speed: 71
                speedSetting: 8
              Fan3:
                powerOn: true
                speed: 72
                speedSetting: 8
              Fan4:
                powerOn: true
                speed: 73
                speedSetting: 8
              Fan5:
                powerOn: true
                speed: 74
                speedSetting: 8
              Fan6:
                powerOn: true
                speed: 75
                speedSetting: 8
              Fan7:
                powerOn: true
                speed: 76
                speedSetting: 8
              Fan8:
                powerOn: true
                speed: 77
                speedSetting: 8
              Fan9:
                powerOn: true
                speed: 78
                speedSetting: 8
              Fan10:
                powerOn: true
                speed: 79
                speedSetting: 8
            filterPanelOpen: false
            boardVoltage: 1145
            fanInputVoltage: 11785
            fanSpeedVoltage: 11654
            lightBank1On: true
            lightBank2On: false
            lightBank3On: false
            fanSpeedOutput: 8
            newFanCalibrated: true
            newFilterCalibrated: true
    PMMStatus:
      title: PMMStatus - Power Management Module Dynamic Information
      description: Current status and environment details of the Power Management Module (PMM)
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - backDoorOpen
            - boostConverterTemperature
            - cpuTemperature
            - current
            - driveDoorOpen
            - fanSpeed
            - faults
            - frontDoorOpen
            - pcbRevision
            - powerBackplaneTemperature1
            - powerBackplaneTemperature2
            - presentPowerSupplies
            - statusLED
            - voltage
          properties:
            backDoorOpen:
              description: If the rear service access door is open
              type: boolean
            boostConverterTemperature:
              description: Boost converter temperature in degrees Celsius
              type: integer
            cpuTemperature:
              description: CPU temperature in degrees Celsius
              type: integer
            current:
              description: Current level of the 24 volt rail in milliamps
              type: integer
            driveDoorOpen:
              description: If the drive access door is open
              type: boolean
            fanSpeed:
              description: The speed of the onboard fan as a percentage of its nominal speed rating
              type: integer
              minimum: 0
              maximum: 255
            faults:
              description: A list of faults detected by the PMM.
              type: array
              items:
                type: string
            frontDoorOpen:
              description: If the front service access door is open
              type: boolean
            pcbRevision:
              type: string
              description: Revision of the PMM PCB.
            powerBackplaneTemperature1:
              description: Power Backplane temperature in degrees Celsius, as read by the first sensor
              type: integer
            powerBackplaneTemperature2:
              description: Power Backplane temperature in degrees Celsius, as read by the second sensor
              type: integer
            presentPowerSupplies:
              description: A list of power supplies present in the library
              type: array
              items:
                type: string
            statusLED:
              $ref: "#/components/schemas/LEDModes"
            voltage:
              description: Voltage level of the 24 volt rail in millivolts
              type: integer
          example:
            backDoorOpen: false
            boostConverterTemperature: 33
            cpuTemperature: 26
            current: 360
            driveDoorOpen: true
            fanSpeed: 0
            faults: [ "Fan Fault" ]
            frontDoorOpen: true
            name: "PMM"
            pcbRevision: "0"
            powerBackplaneTemperature1: 29
            powerBackplaneTemperature2: 30
            presentPowerSupplies: [ "PowerSupply:1", "PowerSupply:2" ]
            status: "OK"
            statusLED: "ON"
            type: "POWER_MANAGEMENT_MODULE"
            voltage: 24030
    SCMDoorState:
      description: Indicates the combined status of all access doors in the library
      type: string
      enum:
        - "OPEN AND LOCKED"
        - "CLOSED AND LOCKED"
        - "INDETERMINATE"
    SCMStatus:
      title: Service Control Module (SCM) Status
      description: |-
        Current status and environment details of the Service Control Module.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - doorState
            - overrideSwitchActive
            - mainPanelOpen
            - rearAccessPanelOpen
            - sideAccessPanelOpen
            - robotPresent
            - robotPowerOn
            - upperLatchOpen
            - lowerLatchOpen
            - bulkExporterPresent
            - solenoidPinPositionExtended
            - chassisID
            - auxSwitch
            - tapLoopback
            - ebiLoopback
            - epmLoopback
            - leftLoopback
            - rightLoopback
            - scmLoopback
            - semLoopback
            - newLightsExist
            - libCommExists
            - tapConnected
            - serviceFramePowerBoardPresent
            - semPresent
            - epmPresent
            - thirdRail24VoltConnected
            - thirdRailGroundConnected
            - serviceFrameRailPower1
            - serviceFrameRailPower2
            - safetyClosed
          properties:
            doorState:
              description: The State of the service bay door
              $ref: "#/components/schemas/SCMDoorState"
            overrideSwitchActive:
              description: Indicates if the override switch is active
              type: boolean
            mainPanelOpen:
              description: Indicates if the main panel on the end of the library is open
              type: boolean
            rearAccessPanelOpen:
              description: Indicates if the rear access panel is open
              type: boolean
            sideAccessPanelOpen:
              description: Indicates if the side HPT access panel is open
              type: boolean
            robotPresent:
              description: Indicates if a robot is present
              type: boolean
            robotPowerOn:
              description: Indicates if the robot power is on
              type: boolean
            upperLatchOpen:
              description: Indicates if the upper latch is open
              type: boolean
            lowerLatchOpen:
              description: Indicates if the lower latch is open
              type: boolean
            bulkExporterPresent:
              description: Indicates if there is a bulk TAP present
              type: boolean
            solenoidPinPositionExtended:
              description: Indicates if solenoid pin position is extended
              type: boolean
            chassisID:
              description: Chassis ID
              type: integer
              format: int32
            auxSwitch:
              description: For internal use only
              type: integer
              format: int32
            tapLoopback:
              description: Indicates that the TAP Loopback is enabled
              type: boolean
            ebiLoopback:
              description: Indicates that the EBI Loopback is enabled
              type: boolean
            epmLoopback:
              description: Indicates that the EPM Loopback is enabled
              type: boolean
            leftLoopback:
              description: Indicates that the Left Loopback is enabled
              type: boolean
            rightLoopback:
              description: Indicates that the Right Loopback is enabled
              type: boolean
            scmLoopback:
              description: Indicates that the SCM Loopback is enabled
              type: boolean
            semLoopback:
              description: Indicates that the SEM Loopback is enabled
              type: boolean
            newLightsExist:
              description: New Light board present. BOA libraries use old Light boards while TFinity libraries use new Light boards.
              type: boolean
            libCommExists:
              description: Indicates if LIBCOMM exists
              type: boolean
            tapConnected:
              description: Indicates if TAP is connected
              type: boolean
            serviceFramePowerBoardPresent:
              description: Indicates if the service frame power board is present
              type: boolean
            semPresent:
              description: Indicates if there is a SEM present
              type: boolean
            epmPresent:
              description: Indicates if EPM is present
              type: boolean
            thirdRail24VoltConnected:
              description: Indicates if third rail 24 volt power is connected
              type: boolean
            thirdRailGroundConnected:
              description: Indicates if third rail ground is connected
              type: boolean
            serviceFrameRailPower1:
              description: Indicates if service frame rail power1 is connected
              type: boolean
            serviceFrameRailPower2:
              description: Indicates if service frame rail power2 is connected
              type: boolean
            safetyClosed:
              description: Indicates if the safety is closed
              type: boolean
          example:
            name: SCM
            doorState: CLOSED AND LOCKED
            overrideSwitchActive: false
            mainPanelOpen: false
            rearAccessPanelOpen: true
            sideAccessPanelOpen: false
            robotPresent: true
            robotPowerOn: true
            upperLatchOpen: false
            lowerLatchOpen: false
            bulkExporterPresent: false
            solenoidPinPositionExtended: true
            chassisID: 7
            auxSwitch: 9
            tapLoopback: false
            ebiLoopback: false
            epmLoopback: false
            leftLoopback: false
            rightLoopback: false
            scmLoopback: true
            semLoopback: false
            newLightsExist: true
            libCommExists: true
            tapConnected: true
            serviceFramePowerBoardPresent: true
            semPresent: true
            epmPresent: true
            thirdRail24VoltConnected: true
            thirdRailGroundConnected: true
            serviceFrameRailPower1: true
            serviceFrameRailPower2: true
            safetyClosed: true
    PowerSupply5V12VStatus:
      title: Status of a 5V/12V power supply
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - statusFlags
            - modelNumber
            - manufacturePartNumber
            - serialNumber
            - modLevel
            - manufacturer
            - countryOfManufacture
            - voltage1Nominal
            - voltage1Value
            - current1Value
            - voltage2Nominal
            - voltage2Value
            - current2Value
            - temperature
          properties:
            statusFlags:
              description: Value of PCM status flags
              type: integer
              minimum: 0
              maximum: 255
            modelNumber:
              description: Model number
              type: string
            manufacturePartNumber:
              description: Manufacturer part number
              type: string
            serialNumber:
              description: Serial number
              type: string
            modLevel:
              description: Mod level
              type: string
            manufacturer:
              description: Manufacturer
              type: string
            countryOfManufacture:
              description: Country where this device was manufactured
              type: string
            voltage1Nominal:
              description: Rail 1 nominal voltage level in millivolts
              type: integer
              format: int32
            voltage1Value:
              description: Rail 1 voltage level in millivolts
              type: integer
              format: int32
            current1Value:
              description: Rail 1 current level in milliamps
              type: integer
              format: int32
            voltage2Nominal:
              description: Rail 2 nominal voltage level in millivolts
              type: integer
              format: int32
            voltage2Value:
              description: Rail 2 voltage level in millivolts
              type: integer
              format: int32
            current2Value:
              description: Rail 2 current level in milliamps
              type: integer
              format: int32
            temperature:
              description: Temperature in degrees Celsius
              type: integer
              format: int32
          example:
            statusFlags: 254
            modelNumber: "90949576"
            manufacturePartNumber: "90948745"
            serialNumber: "123ABC"
            modLevel: "B-002"
            manufacturer: "SPECTRA LOGIC"
            countryOfManufacture: "UNITED STATES"
            voltage1Nominal: 12000
            voltage1Value: 12017
            current1Value: 114
            voltage2Nominal: 5000
            voltage2Value: 5286
            current2Value: 81
            temperature: 30
    PowerSupply24VStatus:
      title: Status of a 24V power supply
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - statusFlags
            - modelNumber
            - manufacturePartNumber
            - serialNumber
            - modLevel
            - manufacturer
            - countryOfManufacture
            - voltage
            - current
            - temperature
          properties:
            statusFlags:
              description: Value of PCM status flags
              type: integer
              minimum: 0
              maximum: 255
            modelNumber:
              description: Model number
              type: string
            manufacturePartNumber:
              description: Manufacturer part number
              type: string
            serialNumber:
              description: Serial number
              type: string
            modLevel:
              description: Mod level
              type: string
            manufacturer:
              description: Manufacturer
              type: string
            countryOfManufacture:
              description: Country where this device was manufactured
              type: string
            voltage:
              description: Voltage level in millivolts
              type: integer
              format: int32
            current:
              description: Current level in milliamps
              type: integer
              format: int32
            temperature:
              description: Temperature in degrees Celsius
              type: integer
              format: int32
          example:
            statusFlags: 254
            modelNumber: "90949876"
            manufacturePartNumber: "90948845"
            serialNumber: "123ABC"
            modLevel: "B-002"
            manufacturer: "SPECTRA LOGIC"
            countryOfManufacture: "UNITED STATES"
            voltage: 24861
            current: 104
            temperature: 25
    PCMSupplyStatus:
      title: Power Control Module Supply Status.
      required:
        - present
        - fault
      properties:
        present:
          description: Indicates if the power supply is present
          type: boolean
        fault:
          description: Indicates if the power supply is faulted
          type: boolean
    PCMStatus:
      title: Power Control Module Status.
      description: |-
        Current status and environment details of the Power Control Module.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - parallelAcPresent
            - primaryAcPresent
            - secondaryAcPresent
            - pcmPresent
            - acCurrent
            - acPrimaryVoltage
            - acSecondaryVoltage
            - power
            - fiveTwelvePower
            - sampleRate
            - samples
            - twelveVolt
            - fiveVolt
            - temperature
            - remoteTemperature
            - supplies
          properties:
            parallelAcPresent:
              description: Indicates if the parallel AC is present
              type: boolean
            primaryAcPresent:
              description: Indicates if the primary AC is present
              type: boolean
            secondaryAcPresent:
              description: Indicates if the secondary AC is present
              type: boolean
            pcmPresent:
              description: Indicates if the PCM is present
              type: boolean
            acCurrent:
              description: AC Current level in milliamps
              type: integer
              format: int32
            acPrimaryVoltage:
              description: AC Primary Voltage level in millivolts
              type: integer
              format: int32
            acSecondaryVoltage:
              description: AC Secondary Voltage level in millivolts
              type: integer
              format: int32
            power:
              description: |-
                Total power draw in Watts over the specified number of samples.
                To get average power, divide by `samples`.
              type: integer
              format: int32
            fiveTwelvePower:
              description: |-
                Combined power draw from the 5V and 12V rails in Watts over the specified number of samples.
                To get average power, divide by `samples`.
              type: integer
              format: int32
            sampleRate:
              description: Sample Rate
              type: integer
              format: int32
            samples:
              description: Sample count
              type: integer
              format: int32
            twelveVolt:
              description: Twelve volt level in millivolts
              type: integer
              format: int32
            fiveVolt:
              description: Five volt level in millivolts
              type: integer
              format: int32
            temperature:
              description: Temperature in degrees Celsius
              type: integer
              format: int32
            remoteTemperature:
              description: Remote temperature in degrees Celsius
              type: integer
              format: int32
            supplies:
              description: Status of each supply
              type: array
              items:
                $ref: "#/components/schemas/PCMSupplyStatus"
          example:
            name: PCM
            parallelAcPresent: true
            primaryAcPresent: true
            secondaryAcPresent: true
            pcmPresent: true
            acCurrent: 6843
            acPrimaryVoltage: 4598
            acSecondaryVoltage: 6789
            power: 9874
            fiveTwelvePower: 4203
            sampleRate: 100
            samples: 245
            twelveVolt: 11874
            fiveVolt: 4890
            temperature: 20
            remoteTemperature: 25
            supplies:
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
              - present: true
                fault: false
    RIMStatus:
      title: RIM Status
      description: |-
        Current status and environment details of the RIM.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - temperature
            - fanOperational
            - linkUpPortA
            - linkUpPortB
          properties:
            temperature:
              description: RIM Temperature in degrees Celsius
              type: integer
              format: int32
            fanOperational:
              description: Indicates if the fan is operational
              type: boolean
            linkUpPortA:
              description: Indicates if port A link is up
              type: boolean
            linkUpPortB:
              description: Indicates if port B link is up
              type: boolean
          example:
            name: RIM
            status: OK
            type: ROBOTICS_INTERFACE_MODULE
            temperature: 35
            fanOperational: true
            linkUpPortA: true
            linkUpPortB: true
    PowerSupply12VStatus:
      title: Status of a 12V power supply
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          required:
            - statusLED
            - fanSpeed
            - voltage
            - current
            - temperature
            - pcbRevision
            - manufacturer
            - modelNumber
          properties:
            statusLED:
              $ref: "#/components/schemas/LEDModes"
            fanSpeed:
              description: Percentage of maximum nominal fan speed. This may be above 100%.
              type: integer
              minimum: 0
              maximum: 255
            voltage:
              description: Voltage level in millivolts
              type: integer
            current:
              description: Current level in milliamps
              type: integer
            temperature:
              description: Temperature in degrees Celsius
              type: integer
            pcbRevision:
              type: string
              description: Revision of the power supply PCB.
            manufacturer:
              description: Manufacturer of the AC/DC power converter
              type: string
            modelNumber:
              description: Model number for the AC/DC power converter
              type: string
          example:
            name: PowerSupply:1
            status: OK
            statusLED: DEVICE_CONTROLLED
            fanSpeed: 43
            voltage: 12077
            current: 2320
            temperature: 30
            pcbRevision: "0"
            manufacturer: "Murata-PS"
            modelNumber: "D1U54P-W-2000-12-HA3C"
    CANRepeaterStatus:
      title: CAN Repeater Status
      description: |-
        Current status and environment details of a CAN Repeater.
      allOf:
        - $ref: '#/components/schemas/BaseFRUStatus'
        - type: object
          properties:
            powerGood:
              type: boolean
              description: Indicates if CAN Repeater power is good.
            pcbRevision:
              type: string
              description: Revision of the CAN Repeater PCB.
          example:
            name: "CANRepeater:2"
            status: "OK"
            type: "CAN_REPEATER"
            powerGood: true
            pcbRevision: "0"
    EnvironmentSensor:
      title: Environment Sensor
      description:
        The current temperature and humidity readings from a sensor
      type: object
      properties:
        tempCelsius:
          type: number
          format: double
          description: The current temperature in degrees Celsius
        relativeHumidityPercent:
          type: number
          format: double
          description: The current humidity as a percentage of the maximum humidity
      required:
        - tempCelsius
        - relativeHumidityPercent
    EnvironmentSummary:
      title: Environment Summary
      description:
        The current temperature and humidity readings from sensors on the library. Sensor availability is dependent on library type as well as presence of High Performance Transporters.
      type: object
      properties:
        chassisTopSensor:
          $ref:
            '#/components/schemas/EnvironmentSensor'
        chassisBottomSensor:
          $ref:
            '#/components/schemas/EnvironmentSensor'
        robot1Sensor:
          $ref:
            '#/components/schemas/EnvironmentSensor'
        robot2Sensor:
          $ref:
            '#/components/schemas/EnvironmentSensor'
    PowerConsumptionList:
      title: Power Consumption List
      description:
        A list of power consumption readings and associated timestamps
      type: object
      properties:
        readings:
          type: array
          items:
            $ref: '#/components/schemas/PowerConsumptionReading'
    PowerConsumptionReading:
      title: Single Power Consumption Reading
      description:
        A reading of the library's power consumption in watts between start and end time.
      type: object
      required:
        - watts
        - startTime
        - endTime
        - source
      properties:
        watts:
          type: number
          format: double
          description: Power consumption in watts
        startTime:
          type: string
          format: date-time
        endTime:
          type: string
          format: date-time
        source:
          type: string
          description: A specific FRU or "Lumos", if this reading is the power consumption of the entire library.
    MessageSummary:
      title: Status Message Summary
      description:
        A summary of current status messages. Includes total number of unread messaged, and number of unread messages grouped by severity.
      type: object
      properties:
        unreadMessages:
          type: integer
          description: Total number of unread messages
        error:
          type: integer
          description: Number of unread error messages
        fatalError:
          type: integer
          description: Number of unread fatal error messages
        info:
          type: integer
          description: Number of unread info messages
        summary:
          type: integer
          description: Number of unread summary messages
        warning:
          type: integer
          description: Number of unread warning messages
      required:
        - unreadMessages
        - fatalError
        - error
        - warning
        - info
        - summary
    SummarySettings:
      title: Summary Settings
      description:
        Settings for which summary information is allowed unauthenticated
      type: object
      properties:
        allowAll:
          type: boolean
          description: Allow all summary endpoints to be used unauthenticated
      required:
        - allowAll
    DrivesSummary:
      description: A summary of the drives in the library. Drives not assigned to a partition are not included in any counts.
      type: object
      properties:
        goodCount:
          description: The number of drives configured correctly and not reporting any failures.
          type: integer
        requiresCleaningCount:
          description: The number of drives that indicate cleaning is required.
          type: integer
        badCount:
          description: The number of drives that indicate failure. Failures include drive display failure values or failures to communicate with the drive.
          type: integer
        missingCount:
          description: The number of drives that are currently assigned to a partition but are not found in the library.
          type: integer
        loadedCount:
          description: The number of drives configured to be in a partition and physically present that are currently loaded with media.
          type: integer
        unloadedCount:
          description: The number of drives configured to be in a partition and physically present that are currently unloaded.
          type: integer
      required:
        - goodCount
        - requiresCleaningCount
        - badCount
        - missingCount
        - loadedCount
        - unloadedCount
    MediaSummary:
      description: A summary of the current media in the library.
      type: object
      properties:
        goodCount:
          description: The number of media in good condition according to the MLM health score.
          type: integer
        averageCount:
          description: The number of media in average condition according to the MLM health score.
          type: integer
        poorCount:
          description: The number of media in poor condition according to the MLM health score.
          type: integer
        undiscoveredCount:
          description: The number of media that have not been discovered by the library and cannot be assigned a health score.
          type: integer
      required:
        - goodCount
        - averageCount
        - poorCount
        - undiscoveredCount
    MovesSummary:
      description: A summary of the current moves in the library.
      type: object
      properties:
        recentMoves:
          description: A list of recent moves ordered by most recent first.
          type: array
          items:
            oneOf:
              - $ref: '#/components/schemas/CleanMove'
              - $ref: '#/components/schemas/ExportMove'
              - $ref: '#/components/schemas/ImportMove'
              - $ref: '#/components/schemas/MediaMove'
          maxItems: 20
      required:
        - recentMoves
    RoboticsSummary:
      description: A summary of robotics in the library.
      type: object
      properties:
        robots:
          type: array
          items:
            type: object
            properties:
              name:
                description: The name of the robot.
                type: string
              status:
                $ref: '#/components/schemas/RoboticsSummaryStatus'
            required:
              - name
              - status
        mountsInLastHour:
          description: The number of drive mounts (slot-to-drive moves) in the last hour.
          type: integer
      required:
        - mountsInLastHour
        - robots
    RoboticsSummaryStatus:
      description: The status of the robot.
      type: string
      enum:
        - "OK"
        - "IMPAIRED"
        - "IN_SERVICE"
        - "INITIALIZING"
        - "UNKNOWN"
    LibraryInfoSummary:
      description: A summary of the library information.
      type: object
      required:
        - name
        - libraryType
      properties:
        name:
          description: The name of the library.
          type: string
        libraryType:
          $ref: '#/components/schemas/LibraryType'
    TAPTypes:
      description: TAP to use to import or export the TeraPack magazine.  Valid destinations are determined by installed hardware.
      type: string
      enum:
        - "MAIN"
        - "LEFT_BULK"
        - "RIGHT_BULK"
        - "MAIN_TOP"
        - "MAIN_BOTTOM"
    BulkTAP:
      description: Bulk TAPs to use to import or export the TeraPack magazine.  Valid destinations are determined by installed hardware.
      type: string
      enum:
        - "LEFT_BULK"
        - "RIGHT_BULK"
    TAPChamberStatus:
      title: TAPChamberStatus
      description: |-
        Current status of a particular chamber within the TAP.
      required:
        - isMagazineInserted
      properties:
        isMagazineInserted:
          type: boolean
          description: Indicates whether the chamber contains a magazine
        magazineType:
          $ref: '#/components/schemas/MediaTypes'
        chamberNumber:
          type: integer
          description: Chamber number. This is shown only when there are more than one chamber available in the TAP.
    TAP:
      title: TAP - Current status of the specified TeraPack Access Port (TAP)
      description: |-
        Current status of the Specified TAP. Any chambers designated for imports and exports on libraries with no TAPs are included here.
      required:
        - tapName
        - isOpen
        - chambers
      properties:
        tapName:
          $ref: '#/components/schemas/TAPTypes'
        isOpen:
          description: Indicates if the TAP is open
          type: boolean
        chambers:
          description: Status of all chambers within the TAP
          type: array
          items:
            $ref: '#/components/schemas/TAPChamberStatus'
        bulkTAPPosition:
          type: string
          enum:
            - "USER"
            - "ROBOT"
            - "UNKNOWN"
        errorState:
          description: Error state of the TAP
          type: string
      example:
        tapName: MAIN_TOP
        isOpen: false
        chambers:
          - isMagazineInserted: true
            magazineType: LTO
    Task:
      title: Task
      description: |-
        Task Manager related information
      required:
        - taskID
        - class
        - type
        - state
        - updated
      properties:
        taskID:
          $ref: "#/components/schemas/TaskID"
        state:
          $ref: "#/components/schemas/TaskStates"
        updated:
          type: string
          format: date-time
          description: The date and time the task was last updated
        percentComplete:
          type: integer
          description: The percentage of the task that is complete
        class:
          $ref: "#/components/schemas/TaskClasses"
        description:
          type: string
          description: Description of the task
        type:
          $ref: "#/components/schemas/TaskTypes"
        tags:
          type: array
          description: User specified tag for the task which can be used in retrieving state. Tags do not need to be unique.
          items:
            type: string
        scheduledStart:
          type: string
          format: date-time
          description: The date and time the task is scheduled to start
        recurringInterval:
          type: string
          description: The interval, in seconds, at which a task is set to recur
        startTime:
          type: string
          format: date-time
          description: Time that the Task started
        endTime:
          type: string
          format: date-time
          description: Ending time of the task
        taskLog:
          type: array
          items:
            type: string
          description: Log of events associated with the task
        resultError:
          $ref: '#/components/schemas/Error'
    TaskID:
      title: TaskID - ID of an Asynchronous task.
      description: |-
        ID of an asynchronous task.
        This is returned as `taskID` from a `GET` request or in the 202 response when starting the task.
      type: string
      example: "a13fbf60-a048-4fe6-a637-1eabc8a9ec60"
    TaskIdList:
      title: TaskIDList
      description: |-
        A list of task IDs.
        This is returned by requests that generate multiple asynchronous operations.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of taskIDs in the list
        value:
          type: array
          items:
            $ref: '#/components/schemas/TaskID'
    TaskList:
      title: TaskList
      description: |-
        Task Manager related information
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        value:
          type: array
          items:
            $ref: '#/components/schemas/Task'
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
      example:
        count: 2
        value:
          - taskID: eb95b54f-fccf-49df-826a-ce122d9018b5
            description: A backup task.
            type: BACKUP
            class: BASIC
            tags: [ ]
            state: FAILED
            percentComplete: 14
            updated: '2021-01-29T19:32:30Z'
            startTime: '2021-01-29T19:32:30Z'
            endTime: '2021-01-29T19:32:30Z'
            taskLog:
              - Starting Backup Creation
            errorResponse: backup limit reached
          - taskID: d6a7026f-75ef-4856-bfb8-6df91b3fc583
            description: A backup task.
            type: BACKUP
            class: BASIC
            tags: [ ]
            state: ABORTED
            percentComplete: 100
            updated: '2021-01-29T19:32:27Z'
            scheduledStart: '2021-01-29T19:32:27Z'
            recurringInterval: '30s'
            startTime: '2021-01-29T19:32:27Z'
            endTime: '2021-01-29T19:32:27Z'
            taskLog:
              - Starting Backup Creation
              - Prepared Backup Directory
              - Generating Backup Metadata
              - Backup Manifest Created
              - Database Backup Created
              - Config Files Copied
              - Backup Created
            errorResponse: ''
          - taskID: d6a7026f-75ef-4856-bfb8-6df91b3fc583
            description: A backup task.
            type: BACKUP
            class: BASIC
            tags: [ ]
            state: ABORTED
            percentComplete: 100
            updated: '2021-01-29T19:32:27Z'
            scheduledStart: '2021-01-29T19:32:27Z'
            recurringInterval: '30s'
            startTime: '2021-01-29T19:32:27Z'
            endTime: '2021-01-29T19:32:27Z'
            taskLog:
              - Starting Backup Creation
              - Prepared Backup Directory
              - Generating Backup Metadata
              - Backup Manifest Created
              - Database Backup Created
              - Config Files Copied
              - Backup Created
            errorResponse: ''
    TaskClasses:
      description: Describes the occurrence rate of a task
      type: string
      enum:
        - "BASIC"
        - "RECURRING"
        - "SCHEDULED"
    TaskTypes:
      title: Task Type
      description: >
        Indicator used for coarse-filtering Tasks
      type: string
      enum:
        - "BACKUP"
        - "MOVE"
        - "DELETE_PARTITION"
        - "DIAGNOSTIC"
        - "FRU_ACTION"
        - "LOG_GATHER"
        - "PACKAGE_UPDATE"
        - "CREATE_PARTITION"
        - "UPDATE_PARTITION"
        - "DRIVE_FIRMWARE_STAGING"
        - "DRIVE_FIRMWARE_COMMITTING"
        - "DEVICE_ADDED_FIRMWARE_CHECKING"
        - "LIBRARY_BOOTUP_FIRMWARE_CHECKING"
        - "INVENTORY_ACTION"
        - "MOTION_FIRMWARE_UPDATE"
    TaskStates:
      title: Task State
      description: >
        Identifies the state of a given Task
        * `UNKNOWN` - UNKNOWN is the default value for any value not listed above. Do not use UNKNOWN as a value for requests.
      type: string
      enum:
        - "ABORTED"
        - "FAILED"
        - "PENDING"
        - "ABORT_PENDING"
        - "RUNNING"
        - "SUCCEEDED"
        - "UNKNOWN"
    TimeInterval:
      description: |-
        A time interval as a string. Valid units are "ns", "us" (or "µs"), "ms", "s", "m", "h"
      type: string
      example:
        "1h30m2s"
    SubscriberID:
      title: SubscriberID - ID of a subscriber to library notifications.
      description: |-
        ID of a subscriber to library notifications.
        This is returned as `subscriberID` from a `GET` request or in the 201 when adding a subscriber
      type: string
      example: "a13fbf60-a048-4fe6-a637-1eabc8a9ec60"
    Subscriber:
      type: object
      required:
        - address
        - smtpAddress
        - companyInfo
        - contactInfo
        - systemInfo
      properties:
        subscriberID:
          $ref: '#/components/schemas/SubscriberID'
        address:
          type: string
          description: |-
            Email address of the recipient
        smtpAddress:
          type: string
          description: |-
            SMTP address of the configured email server, in the form <hostname>:<port>
        companyInfo:
          $ref: '#/components/schemas/SubscriberCompanyInfo'
        contactInfo:
          $ref: '#/components/schemas/SubscriberContactInfo'
        systemInfo:
          $ref: '#/components/schemas/SubscriberSystemInfo'
    SubscriberCompanyInfo:
      description: |-
        Company information for this subscriber
      type: object
      required:
        - name
        - address
      properties:
        name:
          type: string
        address:
          type: string
        location:
          type: string
    SubscriberContactInfo:
      description: |-
        Contact information for the library administrator
      type: object
      required:
        - firstName
        - lastName
        - phoneNumber
        - email
      properties:
        firstName:
          type: string
        lastName:
          type: string
        phoneNumber:
          type: string
        alternatePhone:
          type: string
        email:
          type: string
    SubscriberSystemInfo:
      type: object
      properties:
        os:
          type: string
        backupSoftware:
          type: string
        notes:
          type: string
    UpdateSubscriberRequest:
      type: object
      properties:
        address:
          type: string
          description: |-
            Email address of the recipient
        smtpAddress:
          type: string
          description: |-
            SMTP address of the configured email server
        includeSpectra:
          type: boolean
          description: |-
            Include autosupport@spectralogic.com on the sent auto-support logsets
        companyInfo:
          $ref: '#/components/schemas/SubscriberCompanyInfo'
        contactInfo:
          $ref: '#/components/schemas/SubscriberContactInfo'
        systemInfo:
          $ref: '#/components/schemas/SubscriberSystemInfo'
    SubscriptionSettings:
      type: object
      required:
        - fromAddress
        - driveFailureThresholdPct
        - autoSendCriticalEvents
        - collectDiagnosticData
        - autoSupportSettings
      properties:
        fromAddress:
          type: string
          format: email
          description:
            The email address this library should send from.
        driveFailureThresholdPct:
          type: integer
          minimum: 1
          maximum: 100
          description: |-
            The percentage of drives (inclusive) required to fail to send a library notification
        autoSendCriticalEvents:
          type: boolean
          description: |-
            Send emails automatically whenever a critical event occurs
        collectDiagnosticData:
          type: boolean
          description: |-
            Improve Spectra Logic support by automatically uploading logs to Spectra Logic support servers when a critical event occurs.
        autoSupportSettings:
          type: object
          required:
            - enableAutoSupport
          properties:
            enableAutoSupport:
              type: boolean
              default: false
              description: |-
                Send the auto support logset to autosupport@spectralogic.com
            primarySubscriber:
              description: |-
                The subscriberID of the primary contact for the library. This subscriber's contact information will be 
                included in emails to Spectra Logic support. Emails to Spectra Logic support will use this subscriber's
                SMTP address. This field should be omitted if enableAutoSupport is false.
              $ref: '#/components/schemas/SubscriberID'
    CriticalEventProblemDescription:
      title: Problem Description
      type: object
      required:
        - description
      properties:
        description:
          type: string
        supportTicketNumber:
          type: integer
          description: |
            An optional ticket number to correlate this event with an existing support case. This number must be provided by Spectra Logic Support.
          minimum: 100000
          maximum: 999999
    User:
      required:
        - username
        - userGroup
        - partitions
      properties:
        username:
          description: username
          type: string
        userGroup:
          $ref: "#/components/schemas/GroupNames"
        partitions:
          description: List of partitions the user can access
          type: array
          items:
            type: string
      example:
        username: "a-user"
        userGroup: "OPERATOR"
        partitions: [ "Data Partition" ]
    UserList:
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
        value:
          type: array
          items:
            $ref: '#/components/schemas/User'
    UserRequest:
      required:
        - username
        - password
        - userGroup
      properties:
        username:
          description: username
          type: string
        password:
          description: The password to assign, in clear text
          type: string
          format: password
          maxLength: 72
        userGroup:
          $ref: '#/components/schemas/GroupNames'
        partitions:
          description: |-
            The names of the partitions that the user will have access to.
            This field may only be provided when creating an OPERATOR since
            users in the ADMIN and SUPER_USER groups always have access to all partitions.
          type: array
          items:
            type: string
      example:
        username: "a-user"
        password: "PASSWORD"
        userGroup: "OPERATOR"
        partitions: [ "Data Partition" ]
    GroupNames:
      type: string
      description: |-
        The group to which the user will belong
      enum:
        - "ADMIN"
        - "OPERATOR"
        - "SUPER_USER"
    UserPasswordChangeRequest:
      description: |-
        A request to change a user's password, including the old password for verification
      required:
        - currentPassword
        - newPassword
      properties:
        currentPassword:
          description: The current user's password, in clear text
          type: string
          format: password
          maxLength: 72
        newPassword:
          description: The new password to assign, in clear text
          type: string
          format: password
          maxLength: 72
      example:
        currentPassword: "OLD-PASSWORD"
        newPassword: "NEW-PASSWORD"
    UserChangeRequest:
      properties:
        group:
          $ref: '#/components/schemas/GroupNames'
        partitions:
          description: |-
            The names of the partitions that the user will have access to.
            This field may only be provided for an OPERATOR since users in
            the ADMIN and SUPER_USER groups always have access to all partitions.
          type: array
          items:
            type: string
      example:
        group: "SUPER_USER"
        partitions: [ "New Partition" ]
    MLMList:
      title: MLMList - List of MLM data
      description: |-
        List of Media Lifecycle Management (MLM) data for requested tapes.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
        value:
          type: array
          items:
            $ref: '#/components/schemas/MLMRecord'
    MLMCartridgeTypes:
      description: |-
        The general type of cartridge. One of three values:
          <table>
            <tr><th>cartType</th><th>Description</th></tr>
            <tr><td>DATA</td><td>Regular data cartridge</td></tr>
            <tr><td>CLEAN</td><td>Cleaning cartridge</td></tr>
            <tr><td>WORM</td><td>Write-Once-Read-Many cartridge</td></tr>
          </table>
      type: string
      enum:
        - "CLEAN"
        - "DATA"
        - "WORM"
    MLMMediaGenerations:
      description: >
        The LTO or LDI generation of the tape. Also corresponds to the density.
      type: string
      enum:
        - "JA"
        - "JB"
        - "JC"
        - "JD"
        - "LTO1"
        - "LTO2"
        - "LTO3"
        - "LTO4"
        - "LTO5"
        - "LTO6"
        - "LTO7"
        - "LTO8"
        - "LTOM8"
        - "LTO9"
        - "LTO10"
        - "LTOCleaning"
        - "TSCleaning"
        - "Unknown"
    MLMEncryptionTypes:
      description: >
        The type of encryption used by the drive to encrypt data on this tape. If "UNKNOWN", then the tape has encrypted
        data and either drive encryption is not enabled or is being handled by host software instead of LumOS.
      type: string
      enum:
        - "AES256"
        - "AES256_WITH_COMPRESSION"
        - "COMPRESSION_ONLY"
        - "KMIP_DO_NOT_REUSE_KEYS"
        - "KMIP_REUSE_KEYS"
        - "LTO4_NATIVE"
        - "NONE"
        - "TKLM"
        - "UNKNOWN"
    MLMRecord:
      title: MLMRecord - All MLM data relevant to a tape
      description: |-
        All Media Lifecycle Management (MLM) data stored on the Medium Auxiliary Memory (MAM) of a tape cartridge
      required:
        - MAMReadOnLoad
        - barcode
        - cartType
        - compressionRatioRead
        - compressionRatioWrite
        - isTapeRead
        - lastLoadedPartition
        - manufactured
        - manufacturer
        - manufacturerID
        - maxCapacity
        - mediaGeneration
        - firstWriteLibrary
        - firstWritePartition
        - remainingCapacity
        - remainingMAMCapacity
        - tapeSerial
        - writeProtected
        - export
        - import
      properties:
        MAMReadOnLoad:
          description: |-
            If `true`, a cartridge's MLM data is read whenever it is loaded into a drive.
            If `false`, it is read when the cartridge is unloaded from a drive.
          type: boolean
        barcode:
          description: The barcode of the tape cartridge
          type: string
        bornOn:
          type: string
          description: The CarbideClean certification date of the tape
          format: date
        cartType:
          $ref: '#/components/schemas/MLMCartridgeTypes'
        cleansRemaining:
          description: The remaining number of times this tape can be used to clean a drive (tapes with a `cartType` of `Clean` only)
          type: integer
        compressionRatioRead:
          description: Compression ratio of data read from this tape
          type: integer
        compressionRatioWrite:
          description: Compression ratio of data written to this tape
          type: integer
        healthScore:
          description: |-
            A number from 0 to 100 indicating the overall health of the tape. Generally,
            a score greater than 80 is 'Good', between 50 and 80 is 'Average', and less
            than 50 is 'Poor'.
          type: number
          minimum: 0.0
          maximum: 100.0
          format: double
        isTapeRead:
          description: Whether the tape was read on last load
          type: boolean
        lastLoadedPartition:
          description: The last partition where this tape was loaded into a drive
          type: string
        currentPartition:
          description: The current partition where this tape is located
          type: string
        loadCount:
          description: The total number of times the tape was loaded into a drive
          type: integer
        lifetimeHardWriteErrors:
          description: The total number of non-recoverable write errors experienced on this tape
          type: integer
          format: int64
        lifetimeHardReadErrors:
          description: The total number of non-recoverable read errors experienced on this tape
          type: integer
          format: int64
        manufactured:
          description: The date the tape was manufactured
          type: string
          format: date
        manufacturer:
          type: string
          example: "FUJIFILM"
        manufacturerID:
          description: |-
            Indicates whether the tape was manufactured by Spectra and whether it supports MLM
            <table>
              <tr><th>manufacturerID</th><th>Description</th></tr>
              <tr><td>0</td><td>LTO Spectra Logic</td></tr>
              <tr><td>1</td><td>LTO Customer Conversion</td></tr>
              <tr><td>2</td><td>LTO Non-MLM</td></tr>
              <tr><td>3</td><td>Spectra Logic</td></tr>
              <tr><td>4</td><td>Customer Conversion</td></tr>
              <tr><td>5</td><td>Non-MLM</td></tr>
            </table>
          type: integer
          minimum: 0
          maximum: 5
        maxCapacity:
          description: Storage capacity of the tape in MB
          type: integer
        mediaGeneration:
          $ref: '#/components/schemas/MLMMediaGenerations'
        firstWriteLibrary:
          description: The serial number of the first library to write to the tape
          type: string
        firstWritePartition:
          description: The name of the first partition to write to the tape
          type: string
        remainingCapacity:
          description: Remaining storage space on the tape in MB
          type: integer
        remainingMAMCapacity:
          description: Remaining MAM storage space on the tape in bytes
          type: integer
        tapeSerial:
          description: The serial number of the tape cartridge
          type: string
          example: "1011001EB2"
        writeProtected:
          description: Whether data may be written to the tape
          type: boolean
        readWrite:
          type: object
          properties:
            firstWriteLibrary:
              description: The library in which the tape was first written to
              type: string
            firstWritePartition:
              description: The partition to which the tape belonged when it was first written to
              type: string
            firstWrite:
              description: The time the tape was first written to
              type: string
              format: date-time
            mostRecentWriteLibrary:
              description: The library in which the tape was last written to
              type: string
            mostRecentWritePartition:
              description: The partition to which the tape belonged when it was last written to
              type: string
            mostRecentWrite:
              description: The time the tape was last written to
              type: string
              format: date-time
            firstReadLibrary:
              description: The library in which the tape was first read from
              type: string
            firstReadPartition:
              description: The partition to which the tape belonged when it was first read from
              type: string
            firstRead:
              description: The time the tape was first read from
              type: string
              format: date-time
            mostRecentReadLibrary:
              description: The library in which the tape was last read from
              type: string
            mostRecentReadPartition:
              description: The partition to which the tape belonged when it was last read from
              type: string
            mostRecentRead:
              description: The time the tape was last read from
              type: string
              format: date-time
        carbideClean:
          description: |-
            Metrics provided by Spectra Logic's CarbideClean technology for tapes. Results are only
            available for the first and latest CarbideCleans of the tape.
          type: object
          required:
            - cleanCount
            - firstClean
            - firstCleanDriveID
            - mostRecentClean
            - mostRecentCleanDriveID
            - envTemp
            - envHumidity
          properties:
            cleanCount:
              description: The total number of times this tape was CarbideCleaned
              type: integer
            firstClean:
              description: The time of the first CarbideClean of this tape.
              type: string
              format: date-time
            firstCleanDriveID:
              description: The manufacturer's serial number of the first drive that CarbideCleaned this tape
              type: string
            mostRecentClean:
              description: The time of the last CarbideClean of this tape
              type: string
              format: date-time
            mostRecentCleanDriveID:
              description: The manufacturer's serial number of the last drive that CarbideCleaned this tape
              type: string
            envTemp:
              description: Temperature in Celsius at the time the media was certified
              type: number
            envHumidity:
              description: Humidity (%) at the time the media was certified
              type: integer
        postScan:
          type: object
          required:
            - time
            - failed
            - isQuickScan
          properties:
            time:
              description: The time of the last PostScan verification on the tape
              type: string
              format: date-time
            failed:
              description: Whether the tape passed or failed the last PostScan.
              type: boolean
            isQuickScan:
              description: |-
                Whether the PostScan was a QuickScan or FullScan. A QuickScan only verifies the
                readability of the data on the first wrap, while a FullScan verifies all
                the data on the tape.
              type: boolean
        encryption:
          type: object
          required:
            - encryptionType
            - encryptionGeneration
            - moniker
          properties:
            encryptionType:
              $ref: '#/components/schemas/MLMEncryptionTypes'
            encryptionGeneration:
              description: |-
                For QIP encryption, the version of encryption used to encrypt data on this tape
                <table>
                  <tr><th>Version</th><th>Description</th></tr>
                  <tr><td>0</td><td>Gen3 QIP</td></tr>
                  <tr><td>1</td><td>Gen5 QIP</td></tr>
                </table>
              type: integer
              minimum: 0
              maximum: 1
            moniker:
              description: The moniker of the key used to encrypt data on this tape
              type: string
        export:
          description: Data recorded for each export of the tape
          type: array
          items:
            type: object
            required:
              - user
              - time
            properties:
              user:
                description: The user who requested the export
                type: string
              time:
                description: The time the export occurred
                type: string
                format: date-time
        import:
          description: Data recorded for each import of the tape
          type: array
          items:
            type: object
            required:
              - barcode
              - time
              - user
            properties:
              barcode:
                description: The barcode of the tape
                type: string
              time:
                description: The time of the import
                type: string
                format: date-time
              user:
                description: The user who requested the import
                type: string
        maximumLifetimeTemperature:
          description: Maximum temperature in degrees Celsius during the tape's lifetime. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
        minimumLifetimeTemperature:
          description: Minimum temperature in degrees Celsius during the tape's lifetime. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
        maximumLifetimeHumidity:
          description: Maximum percentage of relative humidity during the tape's lifetime. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
          minimum: 0
          maximum: 100
        minimumLifetimeHumidity:
          description: Minimum percentage of relative humidity during the tape's lifetime. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
          minimum: 0
          maximum: 100
    LoadHealthHistory:
      title: LoadHealthHistory - List of load health history records
      description: |-
        List of health records read as cartridges are unloaded from drives
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
        value:
          type: array
          items:
            $ref: '#/components/schemas/LoadHealthRecord'
    LoadHealthRecord:
      title: LoadHealthRecord - Record of a cartridge being loaded into a drive
      description: Record of a cartridge being loaded into a drive
      required:
        - tapeSerial
        - tapeBarcode
        - alertFlags
        - isValid
        - threadCount
        - writesTotal
        - writeRetriesTotal
        - writeErrorsTotal
        - suspWriteTotal
        - suspWriteErrorsTotal
        - readsTotal
        - readRetriesTotal
        - readErrorsTotal
        - writeHardErrorsTotal
        - readHardErrorsTotal
        - writeSoftErrorsTotal
        - readSoftErrorsTotal
        - unloaded
      properties:
        unloaded:
          description: The time this history entry was added, triggered by the tape being unloaded from the drive
          type: string
          format: date-time
        tapeSerial:
          description: |-
            The serial number of the last tape unloaded from this drive. This value is equal to the
            `MLMRecord.tapeSerial` value for the tape itself.
          type: string
        tapeBarcode:
          description: |-
            The barcode of the last tape unloaded from this drive. This value is equal to the
            `MLMRecord.barcode` value for the tape itself.
          type: string
        driveManufacturerSerial:
          description: The serial number assigned to the drive by its manufacturer
          type: string
        driveSpectraSerial:
          description: The serial number of the FRU assembly containing the drive, assigned by Spectra Logic
          type: string
        driveDisplay:
          description: The character displayed on the Single Character Display (SCD) on the drive at the time of this load
          $ref: "#/components/schemas/DisplayMessage"
        lifetimeDriveHardWriteErrors:
          description: The value of `DLMRecord.lifetimeHardWriteErrors` of the drive at the time of this load
          type: integer
          format: int64
        lifetimeDriveHardReadErrors:
          description: The value of `DLMRecord.lifetimeHardReadErrors` of the drive at the time of this load
          type: integer
          format: int64
        alertFlags:
          description: A list of alerts associated with this tape
          type: array
          items:
            type: string
        isValid:
          description: Whether the health history was read from the tape
          type: boolean
        threadCount:
          description: The total number of times this tape was threaded
          type: integer
        writesTotal:
          description: The total number of writes performed on this tape
          type: integer
        writeRetriesTotal:
          description: The total number of times writes have been retried on this tape
          type: integer
        writeErrorsTotal:
          description: The total number of errors experienced writing data to this tape
          type: integer
        suspWriteTotal:
          description: |-
            The total number of suspended writes experienced on this tape. A write is suspended when a drive determines that it may be unable to successfully write the data at the originally chosen location and attempts the write at a different location.
          type: integer
        suspWriteErrorsTotal:
          description: The total number of times a drive was unable to perform a suspended write to this tape
          type: integer
        readsTotal:
          description: The total number of reads performed on this tape
          type: integer
        readRetriesTotal:
          description: The total number of times reads were retried on this tape
          type: integer
        readErrorsTotal:
          description: The total number of read errors associated with this tape
          type: integer
        writeHardErrorsTotal:
          description: The total number of non-recoverable write errors experienced on this tape
          type: integer
        readHardErrorsTotal:
          description: The total number of non-recoverable read errors experienced on this tape
          type: integer
        writeSoftErrorsTotal:
          description: The total number of write errors experienced on this tape that were recoverable via retrying the write
          type: integer
        readSoftErrorsTotal:
          description: The total number of read errors experienced on this tape that were recoverable via retrying the read
          type: integer
        maximumTemperature:
          description: Maximum temperature in Celsius during the time that the tape was mounted. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
        minimumTemperature:
          description: Minimum temperature in Celsius during the time that the tape was mounted. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
        maximumHumidity:
          description: Maximum percentage of relative humidity during the time that the tape was mounted. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
          minimum: 0
          maximum: 100
        minimumHumidity:
          description: Minimum percentage of relative humidity during the time that the tape was mounted. This may only be supported for LTO-9 or later and TS-1150 or later generation drives.
          type: integer
          minimum: 0
          maximum: 100
    DLMList:
      title: DLMList - List of DLM data
      description: |-
        List of Drive Lifecycle Management (DLM) data for requested tapes.
      required:
        - count
        - value
      properties:
        count:
          type: integer
          description: The count of items in the list
        nextLink:
          type: string
          description: Link to the next page, omitted if this is the last page
        value:
          type: array
          items:
            $ref: '#/components/schemas/DLMRecord'
    DLMRecord:
      title: DLMRecord - All DLM data relevant to a drive
      description: |-
        All Drive Lifecycle Management (DLM) data relevant to a drive
      required:
        - driveManufacturerSerial
        - tapeStuck
      properties:
        driveManufacturerSerial:
          description: The serial number of the drive
          type: string
        tapeStuck:
          description: Whether a tape is currently stuck in the drive
          type: boolean
        lifetimeMediaLoads:
          description: The total number of times media was successfully loaded into this drive
          type: integer
          format: int64
        lifetimeCleaningOps:
          description: |-
            The total number of cleaning operations attempted on this drive, including failed ones
          type: integer
          format: int64
        lifetimePowerOnHours:
          description: The total number of hours this drive was powered on
          type: integer
          format: int64
        lifetimeMediaMotionHours:
          description: |-
            The total number of hours this drive spent processing commands requiring media motion. For example,
            moving tape over the drive head.
          type: integer
          format: int64
        lifetimeMetersTape:
          description: The total meters of tape processed by this drive
          type: integer
          format: int64
        lifetimeMMHAtIncompatibleMediaLoaded:
          description: The total number of Media Motion Hours when an incompatible cartridge was last loaded in the drive
          type: integer
          format: int64
        lifetimePOHAtLastTempAlert:
          description: |-
            The total number of hours the drive was powered on the last time the drive temperature flag was set. This
            corresponds to a `"Temperature"` value appearing in the `alertFlags` list.
          type: integer
          format: int64
        lifetimePOHAtLastPowerAlert:
          description: |-
            The total number of hours the drive was powered on the last time the power consumption alert occurred. This
            corresponds to a `"Power Consumption"` value appearing in the `alertFlags` list.
          type: integer
          format: int64
        mmhSinceLastClean:
          description: Media Motion Hours since the drive was last cleaned
          type: integer
          format: int64
        mmhSinceLastClean2:
          description: Media Motion Hours since the second-to-last time the drive was cleaned
          type: integer
          format: int64
        mmhSinceLastClean3:
          description: Media Motion Hours since the third-to-last time the drive was cleaned
          type: integer
          format: int64
        lifetimePOHAtForcedReset:
          description: |-
            The total hours the drive was powered on at the time of either the last forced reset or the last
            emergency eject
          type: integer
          format: int64
        lifetimePowerCycles:
          description: The total number of power-on events detected by the drive
          type: integer
          format: int64
        lifetimeVolumeLoads:
          description: The total number of successful volume loads this drive performed
          type: integer
          format: int64
        lifetimeHardWriteErrors:
          description: The total number of non-recoverable write errors experienced on this drive
          type: integer
          format: int64
        lifetimeHardReadErrors:
          description: The total number of non-recoverable read errors experienced on this drive
          type: integer
          format: int64
        dutyCycleSampleTimeMS:
          description: |-
            The total time in milliseconds since this statistic was reset. It is used as the base for the following five fields:
            ```
            dutyCycleRead
            dutyCycleWrite
            dutyCycleActive
            dutyCycleVolumeNotPresent
            dutyCycleReady
            ```
          type: integer
          format: int64
        dutyCycleRead:
          description: The percentage of `dutyCycleSampleTimeMS` the drive spent processing read commands
          type: integer
          minimum: 0
          maximum: 100
        dutyCycleWrite:
          description: The percentage of `dutyCycleSampleTimeMS` the drive spent processing write commands
          type: integer
          minimum: 0
          maximum: 100
        dutyCycleActive:
          description: |-
            The percentage of `dutyCycleSampleTimeMS` the drive spent processing any commands requiring the
            tape to be moved
          type: integer
          minimum: 0
          maximum: 100
        dutyCycleVolumeNotPresent:
          description: The percentage of `dutyCycleSampleTimeMS` the drive was empty
          type: integer
          minimum: 0
          maximum: 100
        dutyCycleReady:
          description: The percentage of `dutyCycleSampleTimeMS` the drive was in `READY` status
          type: integer
          minimum: 0
          maximum: 100
        mediumRemovalPrevented:
          description: |-
            Whether removal of a medium was manually prevented (e.g. via some configurable setting).
            Note: This flag is not set by an error condition preventing medium removal.
          type: boolean
        temperatureExceededMax:
          description: |-
            Whether the drive ever exceeded the maximum recommended operating temperature. A `null` value
            indicates that it is unknown whether this drive met this condition.
          type: boolean
    RemoteClientSettings:
      title: RemoteClientSettings - Remote Client Settings
      description: |-
        Settings concerning remote clients of the LumOS API.
      required:
        - allowRemoteImportExport
      properties:
        allowRemoteImportExport:
          description: Allow Import/Export operations from remote clients.
          type: boolean
    MediaMoveMetrics:
      title: MediaMoveMetrics - Metric data about media moves.
      required:
        - readings
      properties:
        readings:
          type: array
          items:
            $ref: '#/components/schemas/MediaMovesReading'
    MediaMovesReading:
      title: MediaMovesReading - Media moves reading.
      description: |-
        The number of moves for the given time range.
      required:
        - moves
        - start
        - end
      properties:
        moves:
          type: integer
          description: The count of moves.
        start:
          type: string
          format: date-time
          description: The beginning of the time range.
        end:
          type: string
          format: date-time
          description: The end of the time range.
    LibraryTemperatureMetrics:
      title: LibraryTemperatureMetrics - Library Temperature Metrics
      properties:
        robot1Readings:
          type: array
          items:
            $ref: '#/components/schemas/TemperatureReading'
        robot2Readings:
          type: array
          items:
            $ref: '#/components/schemas/TemperatureReading'
        chassisTopReadings:
          type: array
          description: Chassis sensors are only present on Cube libraries.
          items:
            $ref: '#/components/schemas/TemperatureReading'
        chassisBottomReadings:
          type: array
          description: Chassis sensors are only present on Cube libraries.
          items:
            $ref: '#/components/schemas/TemperatureReading'
    TemperatureReading:
      title: TemperatureReading - Temperature Reading
      required:
        - start
        - end
      properties:
        start:
          description: The beginning of the time range.
          type: string
          format: date-time
        end:
          description: The end of the time range.
          type: string
          format: date-time
        averageDegreesCelsius:
          description: The average temperature reading for the time range in degrees Celsius. Omitted if data is not available for the time range.
          type: number
          format: double
    LibraryHumidityMetrics:
      title: LibraryHumidityMetrics - Library Humidity Metrics
      properties:
        robot1Readings:
          type: array
          items:
            $ref: '#/components/schemas/HumidityReading'
        robot2Readings:
          type: array
          items:
            $ref: '#/components/schemas/HumidityReading'
        chassisTopReadings:
          type: array
          items:
            $ref: '#/components/schemas/HumidityReading'
        chassisBottomReadings:
          type: array
          items:
            $ref: '#/components/schemas/HumidityReading'
    HumidityReading:
      title: HumidityReading - Humidity Reading
      required:
        - start
        - end
      properties:
        start:
          description: The beginning of the time range.
          type: string
          format: date-time
        end:
          description: The end of the time range.
          type: string
          format: date-time
        averagePercentRelativeHumidity:
          description: The average humidity reading for the time range in percent relative humidity. Omitted if data is not available for the time range.
          type: number
          format: double
  examples:
    dlmList:
      value:
        count: 1
        value:
          - driveManufacturerSerial: 10WT018374
            tapeStuck: false
            fTestFailed: false
            lifetimeMediaLoads: 17
            lifetimeCleaningOps: 2
            lifetimePowerOnHours: 993
            lifetimeMediaMotionHours: 1
            lifetimeMetersTape: 66
            lifetimeMMHAtIncompatibleMediaLoaded: 1
            lifetimeHardWriteErrors: 0
            lifetimeHardReadErrors: 1
            mmhSinceLastClean: 1
            mmhSinceLastClean2: 1
            mmhSinceLastClean3: 1
            lifetimePOHAtForcedReset: 87
            lifetimePowerCycles: 109
            lifetimeVolumeLoads: 17
            dutyCycleSampleTimeMS: 142818530
            dutyCycleRead: 7
            dutyCycleWrite: 4
            dutyCycleActive: 11
            dutyCycleVolumeNotPresent: 8
            dutyCycleReady: 10
            mediumRemovalPrevented: false
            temperatureExceededMax: false
            lifetimePOHAtLastPowerAlert: 85
            lifetimePOHAtLastTempAlert: 19
            loadHistoryEntries:
              - unloaded: "2021-02-02T17:36:10Z"
                tapeSerial: "4191106010"
                tapeBarcode: "LYT7722Q"
                driveManufacturerSerial: "10WT018374"
                lifetimeDriveHardWriteErrors: 0
                lifetimeDriveHardReadErrors: 0
                maximumTemperature: 30
                minimumTemperature: 20
                maximumHumidity: 50
                minimumHumidity: 30
                healthHistory:
                  unloaded: "2021-02-02T17:36:10Z"
                  isValid: true
                  threadCount: 409
                  writesTotal: 2447783
                  writeRetriesTotal: 10
                  writeErrorsTotal: 0
                  suspWriteTotal: 0
                  suspWriteErrorsTotal: 0
                  writeHardErrorsTotal: 0
                  writeSoftErrorsTotal: 0
                  readsTotal: 7511
                  readRetriesTotal: 0
                  readErrorsTotal: 0
                  suspReadTotal: 0
                  suspReadErrorsTotal: 0
                  readHardErrorsTotal: 0
                  readSoftErrorsTotal: 0
                  alertFlags: [ ]
    dlmData:
      value:
        driveManufacturerSerial: 10WT018374
        tapeStuck: false
        fTestFailed: false
        lifetimeMediaLoads: 17
        lifetimeCleaningOps: 2
        lifetimePowerOnHours: 993
        lifetimeMediaMotionHours: 1
        lifetimeMetersTape: 66
        lifetimeMMHAtIncompatibleMediaLoaded: 1
        mmhSinceLastClean: 1
        mmhSinceLastClean2: 1
        mmhSinceLastClean3: 1
        lifetimePOHAtForcedReset: 87
        lifetimePowerCycles: 109
        lifetimeVolumeLoads: 17
        dutyCycleSampleTimeMS: 142818530
        dutyCycleRead: 7
        dutyCycleWrite: 4
        dutyCycleActive: 11
        dutyCycleVolumeNotPresent: 8
        dutyCycleReady: 10
        mediumRemovalPrevented: false
        temperatureExceededMax: false
        lifetimePOHAtLastPowerAlert: 85
        lifetimePOHAtLastTempAlert: 19
        lifetimeHardWriteErrors: 0
        lifetimeHardReadErrors: 0
        loadHistoryEntries:
          - unloaded: "2021-02-02T17:36:10Z"
            tapeSerial: "4191106010"
            tapeBarcode: "LYT7722Q"
            driveManufacturerSerial: "10WT018374"
            lifetimeDriveHardWriteErrors: 0
            lifetimeDriveHardReadErrors: 0
            maximumTemperature: 30
            minimumTemperature: 20
            maximumHumidity: 50
            minimumHumidity: 30
            healthHistory:
              unloaded: "2021-02-02T17:36:10Z"
              isValid: true
              threadCount: 409
              writesTotal: 2447783
              writeRetriesTotal: 10
              writeErrorsTotal: 0
              suspWriteTotal: 0
              suspWriteErrorsTotal: 0
              writeHardErrorsTotal: 0
              writeSoftErrorsTotal: 0
              readsTotal: 7511
              readRetriesTotal: 0
              readErrorsTotal: 0
              suspReadTotal: 0
              suspReadErrorsTotal: 0
              readHardErrorsTotal: 0
              readSoftErrorsTotal: 0
              alertFlags: [ ]
    mlmList:
      value:
        count: 2
        value:
          - MAMReadOnLoad: true
            tapeSerial: 'EY22XNPD75'
            barcode: 'LYT7722Q'
            cartType: CLEAN
            mediaGeneration: 'LTO7'
            maxCapacity: 5722045
            firstWriteLibrary: '2004D00'
            firstWritePartition: 'Data Partition'
            remainingCapacity: 5722045
            remainingMAMCapacity: 3060
            manufacturer: 'IBM'
            manufacturerID: 5
            manufactured: '2019-03-28'
            loadCount: 336
            healthScore: 89.0
            isTapeRead: false
            writeProtected: false
            compressionRatioRead: 1
            compressionRatioWrite: 1
            lastLoadedPartition: "Data Partition"
            maximumTemperature: 40
            minimumTemperature: 30
            maximumHumidity: 50
            minimumHumidity: 45
            carbideClean:
              cleanCount: 7
              firstClean: '2020-04-11T07:00:10Z'
              firstCleanDriveID: 'NJJ8001'
              mostRecentClean: '2021-01-08T16:44:01Z'
              mostRecentCleanDriveID: 'NJJ9876'
              envTemp: 18
              envHumidity: 49
            healthHistory: [ ]
            import:
              - user: "admin"
                time: "2021-01-29T07:19:25Z"
                barcode: "LYT7722Q"
            export: [ ]
          - MAMReadOnLoad: false
            tapeSerial: 'EY22XNPD75'
            barcode: 'LYT7722Q'
            cartType: DATA
            mediaGeneration: 'LTO7'
            maxCapacity: 5722045
            firstWriteLibrary: '2004D00'
            firstWritePartition: 'Data Partition'
            remainingCapacity: 5722045
            remainingMAMCapacity: 3060
            manufacturer: FUJIFILM
            manufacturerID: 5
            manufactured: '2019-03-13'
            loadCount: 336
            healthScore: 89.0
            isTapeRead: true
            writeProtected: false
            compressionRatioRead: 1
            compressionRatioWrite: 1
            maximumTemperature: 40
            minimumTemperature: 30
            maximumHumidity: 50
            minimumHumidity: 45
            lastLoadedPartition: "Data Partition"
            readWrite:
              firstWriteLibrary: '2004D00'
              firstWritePartition: 'Data Partition'
              firstWrite: '2021-01-04T08:34:51Z'
              mostRecentWriteLibrary: '2004D00'
              mostRecentWritePartition: 'Data Partition'
              mostRecentWrite: '2021-01-24T18:34:51Z'
              firstReadLibrary: '2004D00'
              firstReadPartition: 'Data Partition'
              firstRead: '2021-01-04T08:39:25Z'
              mostRecentReadLibrary: '2004D00'
              mostRecentReadPartition: 'Data Partition'
              mostRecentRead: '2021-01-29T07:19:25Z'
            postScan:
              time: '2021-01-29T07:19:25Z'
              failed: false
              isQuickScan: true
            encryption:
              encryptionType: 'AES256'
              encryptionGeneration: 1
              moniker: 'My Encryption Key'
            export:
              - user: "admin"
                time: '2021-01-29T07:19:25Z'
              - user: "admin"
                time: '2021-02-05T07:19:25Z'
            import:
              - user: "admin"
                time: "2021-01-29T07:19:25Z"
                barcode: "LYT7722Q"
              - user: "admin"
                time: "2021-01-29T07:19:25Z"
                barcode: "LYT7722Q"
            healthHistory:
              - isValid: true
                alertFlags: [ 'Hard Error', 'Read Warning', 'Unsupported Format' ]
                threadCount: 336
                writesTotal: 1221551
                writeRetriesTotal: 35
                writeErrorsTotal: 11
                suspWriteTotal: 7
                suspWriteErrorsTotal: 3
                readsTotal: 7988499
                readRetriesTotal: 894
                readErrorsTotal: 104
                writeHardErrorsTotal: 4
                readHardErrorsTotal: 22
                writeSoftErrorsTotal: 9
                readSoftErrorsTotal: 56
                unloaded: '2021-01-28T21:10:52Z'
    mlmDataDataTape:
      value:
        MAMReadOnLoad: true
        tapeSerial: 'EY22XNPD75'
        barcode: 'LYT7722Q'
        cartType: DATA
        mediaGeneration: 'LTO7'
        maxCapacity: 5722045
        firstWriteLibrary: '2004D00'
        firstWritePartition: 'Data Partition'
        remainingCapacity: 5722045
        remainingMAMCapacity: 3060
        manufacturer: FUJIFILM
        manufacturerID: 5
        manufactured: '2019-03-24'
        loadCount: 336
        healthScore: 89.0
        isTapeRead: true
        writeProtected: false
        compressionRatioRead: 1
        compressionRatioWrite: 1
        maximumTemperature: 40
        minimumTemperature: 30
        maximumHumidity: 50
        minimumHumidity: 45
        lastLoadedPartition: "Data Partition"
        readWrite:
          firstWriteLibrary: '2004D00'
          firstWritePartition: 'Data Partition'
          firstWrite: '2021-01-04T08:34:51Z'
          mostRecentWriteLibrary: '2004D00'
          mostRecentWritePartition: 'Data Partition'
          mostRecentWrite: '2021-01-24T18:34:51Z'
          firstReadLibrary: '2004D00'
          firstReadPartition: 'Data Partition'
          firstRead: '2021-01-04T08:39:25Z'
          mostRecentReadLibrary: '2004D00'
          mostRecentReadPartition: 'Data Partition'
          mostRecentRead: '2021-01-29T07:19:25Z'
        postScan:
          time: '2021-01-29T07:19:25Z'
          failed: false
          isQuickScan: true
        encryption:
          encryptionType: 'AES256'
          encryptionGeneration: 1
          moniker: 'My Encryption Key'
        export:
          - user: "admin"
            time: '2021-01-29T07:19:25Z'
          - user: "admin"
            time: '2021-02-05T07:19:25Z'
        import:
          - user: "admin"
            time: "2021-01-29T07:19:25Z"
            barcode: "LYT7722Q"
          - user: "admin"
            time: "2021-01-29T07:19:25Z"
            barcode: "LYT7722Q"
        healthHistory:
          - isValid: true
            alertFlags: [ 'Hard Error', 'Read Warning', 'Unsupported Format' ]
            threadCount: 336
            writesTotal: 1221551
            writeRetriesTotal: 35
            writeErrorsTotal: 11
            suspWriteTotal: 7
            suspWriteErrorsTotal: 3
            readsTotal: 7988499
            readRetriesTotal: 894
            readErrorsTotal: 104
            writeHardErrorsTotal: 4
            readHardErrorsTotal: 22
            writeSoftErrorsTotal: 9
            readSoftErrorsTotal: 56
            unloaded: '2021-01-28T21:10:52Z'
    mlmDataCleaningTape:
      value:
        MAMReadOnLoad: true
        tapeSerial: 'EY22XNPD75'
        cartType: CLEAN
        barcode: 'LYT7722Q'
        mediaGeneration: 'LTO7'
        maxCapacity: 5722045
        firstWriteLibrary: '2004D00'
        firstWritePartition: 'Data Partition'
        remainingCapacity: 5722045
        remainingMAMCapacity: 3060
        manufacturer: 'IBM'
        manufacturerID: 5
        manufactured: '2019-03-26'
        loadCount: 336
        healthScore: 89.0
        isTapeRead: false
        writeProtected: false
        compressionRatioRead: 0
        compressionRatioWrite: 0
        lastLoadedPartition: ""
        maximumTemperature: 40
        minimumTemperature: 30
        maximumHumidity: 50
        minimumHumidity: 45
        healthHistory: [ ]
        carbideClean:
          cleanCount: 7
          firstClean: '2020-04-11T07:00:10Z'
          firstCleanDriveID: 'NJJ8001'
          mostRecentClean: '2021-01-08T16:44:01Z'
          mostRecentCleanDriveID: 'NJJ9876'
          envTemp: 18
          envHumidity: 49
        import:
          - user: "admin"
            time: "2021-01-29T07:19:25Z"
            barcode: "CLN7722Q"
        export: [ ]
security:
  - BearerAuth: [ ]
