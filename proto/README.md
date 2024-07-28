# proto

These shared protobuf definitions are used to pass data on the wire.

## vs code setup

Using vscode-proto3, we can build on save, which is a bit faster/better
user experience. Install the plugin, and use this snippet, updating
```
    "protoc": {
        "path": "path_to_protoc_executable",
        "compile_on_save": true,
        "options": [
            "--proto_path=${workspaceRoot}/proto/proto",
            "--python_betterproto_out=${workspaceRoot}/shared/nk_shared"
        ]
    }
```

## watcher

There is a filesystem based watcher to build, which can be invoked with
`make watch`
