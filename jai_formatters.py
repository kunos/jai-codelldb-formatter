import math

import lldb


def __lldb_init_module(debugger, dict):
    debugger.HandleCommand(
        "type summary add --recognizer-function --python-function jai_formatters.jai_string_summary jai_formatters.is_string_type"
    )

    debugger.HandleCommand(
        "type summary add --recognizer-function --python-function jai_formatters.array_summary jai_formatters.is_array_type"
    )
    debugger.HandleCommand(
        "type synth add --recognizer-function --python-class jai_formatters.ArrayChildProvider jai_formatters.is_array_type"
    )


def is_array_type(t, internal_dict):
    return t.name.startswith("array_")


def array_summary(value, internal_dict):
    value = value.GetNonSyntheticValue()
    type_name = value.GetType().GetDisplayTypeName()

    if type_name.startswith("array"):  # slice
        len = value.GetChildMemberWithName("count").unsigned
        return f"{type_name} (count:{len})"

    return type_name


def is_string_type(t, internal_dict):
    return t.name == "string"


def jai_string_summary(valobj, internal_dict):
    # Assuming a Jai string struct has members named 'count' and 'data'

    count = valobj.GetChildMemberWithName("count").GetValueAsUnsigned(0)
    print(valobj.GetChildMemberWithName("data"))
    ptr_data = valobj.GetChildMemberWithName("data").GetValueAsUnsigned(0)

    if ptr_data == 0:
        return False

    error = lldb.SBError()
    string_data = valobj.process.ReadMemory(ptr_data, count, error)

    return '"{}"'.format(string_data.decode("utf-8"))


class ArrayChildProvider:
    CHUNK_COUNT = 2000

    def __init__(self, val, dict):
        self.val = val
        self.update()

    def update(self):
        val = self.val

        self.len = val.GetChildMemberWithName("count").unsigned
        self.data_val = val.GetChildMemberWithName("data")
        assert self.data_val.type.is_pointer

        is_chunked = self.len > ArrayChildProvider.CHUNK_COUNT
        self.chunked_len = (
            0
            if not is_chunked
            else math.ceil(self.len / ArrayChildProvider.CHUNK_COUNT)
        )

        return False

    def num_children(self):
        return self.chunked_len if self.chunked_len > 0 else self.len

    def get_child_at_index(self, index):
        length = self.num_children()
        assert index >= 0 and index < length

        first = self.data_val.deref

        if self.chunked_len > 0:
            chunk_size = ArrayChildProvider.CHUNK_COUNT

            array_len = min(chunk_size, self.len - index * chunk_size)
            arr_type = first.type.GetArrayType(array_len)
            offset = index * first.size * chunk_size

            range_start = index * chunk_size

            return self.data_val.CreateChildAtOffset(
                f"[{range_start}..<{range_start + array_len}]", offset, arr_type
            )

        offset = index * first.size
        return self.data_val.CreateChildAtOffset(f"[{index}]", offset, first.type)
