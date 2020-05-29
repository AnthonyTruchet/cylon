from pytwisterx.common.join_config cimport CJoinType
from pytwisterx.common.join_config cimport CJoinAlgorithm
from pytwisterx.common.join_config cimport CJoinConfig
cimport cython
from enum import Enum


class PJoinAlgorithm(Enum):
    SORT = "sort"
    HASH = "hash"


class PJoinType(Enum):
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    OUTER = "fullouter"


cpdef enum JoinType:
    INNER = CJoinType.CINNER
    LEFT = CJoinType.CLEFT
    RIGHT = CJoinType.CRIGHT
    OUTER = CJoinType.COUTER

cpdef enum JoinAlgorithm:
    SORT = CJoinAlgorithm.CSORT
    HASH = CJoinAlgorithm.CHASH

cdef class JoinConfig:
    cdef CJoinConfig *jcPtr
    cdef CJoinType jtPtr
    cdef CJoinAlgorithm jaPtr

    def __cinit__(self, join_type: str, join_algorithm: str, left_column_index: int, right_column_index: int):
        if join_type is not None and join_algorithm is not None and left_column_index is not None and right_column_index is not None:
            self._get_join_config(join_type=join_type, join_algorithm=join_algorithm,
                                  left_column_index=left_column_index,
                                  right_column_index=right_column_index)

    cdef _get_join_config(self, join_type: str, join_algorithm: str, left_column_index: int,
                          right_column_index: int):
        if left_column_index is None or right_column_index is None:
            raise Exception("Join Column index not provided")

        if join_algorithm is None:
            join_algorithm = PJoinAlgorithm.HASH.value

        if join_algorithm == PJoinAlgorithm.HASH.value:

            if join_type == PJoinType.INNER.value:
                self.jcPtr = new CJoinConfig(CJoinType.CINNER, left_column_index, right_column_index,
                                             CJoinAlgorithm.CHASH)
            elif join_type == PJoinType.LEFT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CLEFT, left_column_index, right_column_index,
                                             CJoinAlgorithm.CHASH)
            elif join_type == PJoinType.RIGHT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CRIGHT, left_column_index, right_column_index,
                                             CJoinAlgorithm.CHASH)
            elif join_type == PJoinType.OUTER.value:
                self.jcPtr = new CJoinConfig(CJoinType.COUTER, left_column_index, right_column_index,
                                             CJoinAlgorithm.CHASH)
            else:
                raise ValueError("Unsupported Join Type {}".format(join_type))

        elif join_algorithm == PJoinAlgorithm.SORT.value:

            if join_type == PJoinType.INNER.value:
                self.jcPtr = new CJoinConfig(CJoinType.CINNER, left_column_index, right_column_index,
                                             CJoinAlgorithm.CSORT)
            elif join_type == PJoinType.LEFT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CLEFT, left_column_index, right_column_index,
                                             CJoinAlgorithm.CSORT)
            elif join_type == PJoinType.RIGHT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CRIGHT, left_column_index, right_column_index,
                                             CJoinAlgorithm.CSORT)
            elif join_type == PJoinType.OUTER.value:
                self.jcPtr = new CJoinConfig(CJoinType.COUTER, left_column_index, right_column_index,
                                             CJoinAlgorithm.CSORT)
            else:
                raise ValueError("Unsupported Join Type {}".format(join_type))
        else:
            if join_type == PJoinType.INNER.value:
                self.jcPtr = new CJoinConfig(CJoinType.CINNER, left_column_index, right_column_index)
            elif join_type == PJoinType.LEFT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CLEFT, left_column_index, right_column_index)
            elif join_type == PJoinType.RIGHT.value:
                self.jcPtr = new CJoinConfig(CJoinType.CRIGHT, left_column_index, right_column_index)
            elif join_type == PJoinType.OUTER.value:
                self.jcPtr = new CJoinConfig(CJoinType.COUTER, left_column_index, right_column_index)
            else:
                raise ValueError("Unsupported Join Type {}".format(join_type))

    @property
    def join_type(self) -> JoinType:
        self.jtPtr = self.jcPtr.GetType()
        return self.jtPtr

    @property
    def join_algorithm(self) -> JoinAlgorithm:
        self.jaPtr = self.jcPtr.GetAlgorithm()
        return self.jaPtr

    @property
    def left_index(self) -> int:
        return self.jcPtr.GetLeftColumnIdx()

    @property
    def right_index(self)-> int:
        return self.jcPtr.GetRightColumnIdx()