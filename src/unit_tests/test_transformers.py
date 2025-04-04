#!/usr/bin/python3
# SPDX-License-Identifier: MIT

try:

    from testcrush import transformers
    from testcrush import zoix

except ModuleNotFoundError:

    import sys
    sys.path.append("..")
    from testcrush import transformers
    from testcrush import zoix

import unittest
import lark


class FaultReportFaultListTransformerTest(unittest.TestCase):

    def get_parser(self):

        factory = transformers.FaultReportTransformerFactory()
        return factory("FaultList")

    def test_stuck_at_fault_list(self):

        parser = self.get_parser()


        fault_list_sample = r"""
            FaultList SAF {
                <  1> ON 0 {PORT "tb.dut.subunit_a.subunit_b.cellA.ZN"}(* "test1"->PC=30551073; "test1"->time="45ns"; *)
                    -- 1 {PORT "tb.dut.subunit_a.subunit_b.cellA.A1"}
                    -- 1 {PORT "tb.dut.subunit_a.subunit_b.cellA.A2"}
                    -- 0 {PORT "tb.dut.subunit_a.subunit_b.operand_b[27:3]"}
            }
        """
        expected_faults = [
            zoix.Fault(fault_status='ON', fault_type='0', fault_sites=['tb.dut.subunit_a.subunit_b.cellA.ZN'], fault_attributes={'PC': '30551073', 'time': '45ns'}),
            zoix.Fault(fault_status='ON', fault_type='1', fault_sites=['tb.dut.subunit_a.subunit_b.cellA.A1']),
            zoix.Fault(fault_status='ON', fault_type='1', fault_sites=['tb.dut.subunit_a.subunit_b.cellA.A2']),
            zoix.Fault(fault_status='ON', fault_type='0', fault_sites=['tb.dut.subunit_a.subunit_b.operand_b[27:3]'])
        ]

        fault_list = parser.parse(fault_list_sample)

        # Manually resolve the fault equivalences
        expected_faults[0].equivalent_faults = 4
        expected_faults[1].equivalent_to = expected_faults[0]
        expected_faults[2].equivalent_to = expected_faults[0]
        expected_faults[3].equivalent_to = expected_faults[0]

        self.assertEqual(fault_list, expected_faults)

    def test_transition_delay_fault_list(self):

        parser = self.get_parser()

        fault_list_sample = r"""
            FaultList TDF {
                <  1> NN F {PORT "tb.dut.subunit_c.U1528.CI"}
                <  1> ON R {PORT "tb.dut.subunit_c.U1528.CO"}(* "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- R {PORT "tb.dut.subunit_c.U28.A"}
                <  1> ON F {PORT "tb.dut.subunit_c.U1528.CO"}(* "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- F {PORT "tb.dut.subunit_c.U28.A"}
                <  1> ON R {PORT "tb.dut.subunit_c.U1528.S"}(*  "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- R {PORT "tb.dut.subunit_c.U27.A"}
                <  1> ON F {PORT "tb.dut.subunit_c.U1528.S"}(*  "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- F {PORT "tb.dut.subunit_c.U27.A"}
            }
        """
        expected_faults = [
            zoix.Fault(fault_status='NN', fault_type='F', fault_sites=['tb.dut.subunit_c.U1528.CI']),
            zoix.Fault(fault_status='ON', fault_type='R', fault_sites=['tb.dut.subunit_c.U1528.CO'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='R', fault_sites=['tb.dut.subunit_c.U28.A']),
            zoix.Fault(fault_status='ON', fault_type='F', fault_sites=['tb.dut.subunit_c.U1528.CO'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='F', fault_sites=['tb.dut.subunit_c.U28.A']),
            zoix.Fault(fault_status='ON', fault_type='R', fault_sites=['tb.dut.subunit_c.U1528.S'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='R', fault_sites=['tb.dut.subunit_c.U27.A']),
            zoix.Fault(fault_status='ON', fault_type='F', fault_sites=['tb.dut.subunit_c.U1528.S'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='F', fault_sites=['tb.dut.subunit_c.U27.A'])
        ]

        # Manually resolve the fault equivalences
        expected_faults[1].equivalent_faults = 2
        expected_faults[2].equivalent_to = expected_faults[1]
        expected_faults[3].equivalent_faults = 2
        expected_faults[4].equivalent_to = expected_faults[3]
        expected_faults[5].equivalent_faults = 2
        expected_faults[6].equivalent_to = expected_faults[5]
        expected_faults[7].equivalent_faults = 2
        expected_faults[8].equivalent_to = expected_faults[7]

        fault_list = parser.parse(fault_list_sample)

        self.assertEqual(fault_list, expected_faults)

    def test_small_delay_defects_fault_list(self):

        parser = self.get_parser()

        fault_list_sample = r"""
            FaultList TDF {
                <  1> NN F (6.532ns) {PORT "tb.dut.subunit_c.U1528.CI"}
                <  1> ON R (6.423ns) {PORT "tb.dut.subunit_c.U1528.CO"}(* "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- R (6.6123ns) {PORT "tb.dut.subunit_c.U28.A"}
                <  1> ON F (5.532ns) {PORT "tb.dut.subunit_c.U1528.CO"}(* "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- F (6.532ns) {PORT "tb.dut.subunit_c.U28.A"}
                <  1> ON R (2.232ns) {PORT "tb.dut.subunit_c.U1528.S"}(*  "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- R (9.722ns) {PORT "tb.dut.subunit_c.U27.A"}
                <  1> ON F (9.432ns) {PORT "tb.dut.subunit_c.U1528.S"}(*  "test1"->PC_IF=00000d1c; "test1"->sim_time="   8905ns"; *)
                      -- F (1.532ns) {PORT "tb.dut.subunit_c.U27.A"}
                      -- ~ (6,4,26) {FLOP "tb.dut.subunit_d.reg_q[0]"}
            }
        """

        fault_list = parser.parse(fault_list_sample)

        expected_faults = [
            zoix.Fault(fault_status='NN', fault_type='F', timing_info=['6.532ns'], fault_sites=['tb.dut.subunit_c.U1528.CI']),
            zoix.Fault(fault_status='ON', fault_type='R', timing_info=['6.423ns'], fault_sites=['tb.dut.subunit_c.U1528.CO'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='R', timing_info=['6.6123ns'], fault_sites=['tb.dut.subunit_c.U28.A']),
            zoix.Fault(fault_status='ON', fault_type='F', timing_info=['5.532ns'], fault_sites=['tb.dut.subunit_c.U1528.CO'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='F', timing_info=['6.532ns'], fault_sites=['tb.dut.subunit_c.U28.A']),
            zoix.Fault(fault_status='ON', fault_type='R', timing_info=['2.232ns'], fault_sites=['tb.dut.subunit_c.U1528.S'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='R', timing_info=['9.722ns'], fault_sites=['tb.dut.subunit_c.U27.A']),
            zoix.Fault(fault_status='ON', fault_type='F', timing_info=['9.432ns'], fault_sites=['tb.dut.subunit_c.U1528.S'], fault_attributes={'PC_IF': '00000d1c', 'sim_time': '8905ns'}),
            zoix.Fault(fault_status='ON', fault_type='F', timing_info=['1.532ns'], fault_sites=['tb.dut.subunit_c.U27.A']),
            zoix.Fault(fault_status='ON', fault_type='~', timing_info=['6', '4', '26'], fault_sites=['tb.dut.subunit_d.reg_q[0]'])

        ]

        # Manually resolve the fault equivalences
        expected_faults[1].equivalent_faults = 2
        expected_faults[2].equivalent_to = expected_faults[1]
        expected_faults[3].equivalent_faults = 2
        expected_faults[4].equivalent_to = expected_faults[3]
        expected_faults[5].equivalent_faults = 2
        expected_faults[6].equivalent_to = expected_faults[5]
        expected_faults[7].equivalent_faults = 3
        expected_faults[8].equivalent_to = expected_faults[7]
        expected_faults[9].equivalent_to = expected_faults[7]

        self.assertEqual(fault_list, expected_faults)


class FaultReportStatusGroupsTransformerTest(unittest.TestCase):

    def get_parser(self):

        factory = transformers.FaultReportTransformerFactory()
        return factory("StatusGroups")

    def test_no_leq_group_section(self):

        parser = self.get_parser()

        status_groups_sample = r"""
        StatusGroups {
            SA "Safe" (UT, UB, UR, UU);
            SU "Safe Unobserved" (NN, NC, NO, NT);
            DA "Dangerous Assumed" (HA, HM, HT, OA, OZ, IA, IP, IF, IX);
            DN "Dangerous Not Diagnosed" (PN, ON, PP, OP, NP, AN, AP);
            DD "Dangerous Diagnosed" (PD, OD, ND, AD);
        }
        """

        groups = parser.parse(status_groups_sample)
        expected_groups = {'SA': ['UT', 'UB', 'UR', 'UU'],
                           'SU': ['NN', 'NC', 'NO', 'NT'],
                           'DA': ['HA', 'HM', 'HT', 'OA', 'OZ', 'IA', 'IP', 'IF', 'IX'],
                           'DN': ['PN', 'ON', 'PP', 'OP', 'NP', 'AN', 'AP'],
                           'DD': ['PD', 'OD', 'ND', 'AD']}

        self.assertEqual(groups, expected_groups)

    def test_leq_group_section(self):

        parser = self.get_parser()

        status_groups_sample = r"""
        StatusGroups {
            SA "Safe" (UT < UB < UR UU);
            SU "Safe Unobserved" (NN < NC < NO < NT);
            DA "Dangerous Assumed" (HA < HM < HT < OA < OZ < IA < IP < IF < IX);
            DN "Dangerous Not Diagnosed" (PN < ON < PP < OP < NP < AN < AP);
            DD "Dangerous Diagnosed" (PD < OD < ND < AD);
        }
        """

        groups = parser.parse(status_groups_sample)
        expected_groups = {'SA': ['UT', 'UB', 'UR', 'UU'],
                           'SU': ['NN', 'NC', 'NO', 'NT'],
                           'DA': ['HA', 'HM', 'HT', 'OA', 'OZ', 'IA', 'IP', 'IF', 'IX'],
                           'DN': ['PN', 'ON', 'PP', 'OP', 'NP', 'AN', 'AP'],
                           'DD': ['PD', 'OD', 'ND', 'AD']}

        self.assertEqual(groups, expected_groups)

class FaultReportCoverageTransformerTest(unittest.TestCase):

    def get_parser(self):

        factory = transformers.FaultReportTransformerFactory()
        return factory("Coverage")

    def test_coverage_str_no_quotes_lhs(self):

        parser = self.get_parser()

        coverage_sample = r"""
        Coverage {
            Coverage_1 = "AA + BB + CC";
            Coverage_2 = "(DD + DN)/(NA + DA + DN + DD + SU)";
         }
        """

        coverage = parser.parse(coverage_sample)
        expected_coverage = {'Coverage_1': 'AA + BB + CC', 'Coverage_2': '(DD + DN)/(NA + DA + DN + DD + SU)'}
        self.assertEqual(coverage, expected_coverage)

    def test_coverage_str_with_quotes_lhs(self):

        parser = self.get_parser()

        coverage_sample = r"""
        Coverage {
            "Coverage_1" = "AA + BB + CC";
            "Coverage_2" = "(DD + DN)/(NA + DA + DN + DD + SU)";
         }
        """

        coverage = parser.parse(coverage_sample)
        expected_coverage = {'Coverage_1': 'AA + BB + CC', 'Coverage_2': '(DD + DN)/(NA + DA + DN + DD + SU)'}
        self.assertEqual(coverage, expected_coverage)

    def test_coverage_with_format_specifiers_rhs(self):

        parser = self.get_parser()

        coverage_sample = r"""
        Coverage {
            "Coverage_1" = "FLT(AA + BB + CC)";
            Coverage_2 = "PCT((DD + DN)/(NA + DA + DN + DD + SU))";
            Coverage_3 = "INT(FF+CC*2)";
         }
        """

        coverage = parser.parse(coverage_sample)
        expected_coverage = {'Coverage_1': '(AA + BB + CC)',
                             'Coverage_2': '((DD + DN)/(NA + DA + DN + DD + SU))',
                             'Coverage_3': '(FF+CC*2)'}
        self.assertEqual(coverage, expected_coverage)

    def test_coverage_with_power_operator_rhs(self):

        parser = self.get_parser()

        coverage_sample = r"""
        Coverage {
            "Coverage_1" = "FLT(AA ^ BB ^ CC)";
         }
        """
        coverage = parser.parse(coverage_sample)
        expected_coverage = {'Coverage_1': '(AA ** BB ** CC)'}
        self.assertEqual(coverage, expected_coverage)

class TraceTransformerCV32E40PTest(unittest.TestCase):

    def get_parser(self):

        factory = transformers.TraceTransformerFactory()
        return factory("CV32E40P")

    def test_doc_example(self):

        parser = self.get_parser()

        trace_sample = r"""Time          Cycle      PC       Instr    Decoded instruction Register and memory contents
130         61 00000150 4481     c.li    x9,0        x9=0x00000000
132         62 00000152 00008437 lui     x8,0x8      x8=0x00008000
134         63 00000156 fff40413 addi    x8,x8,-1    x8:0x00008000  x8=0x00007fff
136         64 0000015a 8c65     c.and   x8,x9       x8:0x00007fff  x9:0x00000000  x8=0x00000000
142         67 0000015c c622     c.swsp  x8,12(x2)   x2:0x00002000  x8:0x00000000 PA:0x0000200c store:0x00000000  load:0xffffffff
"""
        csv_lines = parser.parse(trace_sample)

        expected_csv_lines = ['Time,Cycle,PC,Instr,Decoded instruction,Register and memory contents',
                              '130,61,00000150,4481,"c.li x9,0","x9=0x00000000"',
                              '132,62,00000152,00008437,"lui x8,0x8","x8=0x00008000"',
                              '134,63,00000156,fff40413,"addi x8,x8,-1","x8:0x00008000, x8=0x00007fff"',
                              '136,64,0000015a,8c65,"c.and x8,x9","x8:0x00007fff, x9:0x00000000, x8=0x00000000"',
                              '142,67,0000015c,c622,"c.swsp x8,12(x2)","x2:0x00002000, x8:0x00000000, PA:0x0000200c, store:0x00000000, load:0xffffffff"']

        self.assertEqual(csv_lines, expected_csv_lines)

    def test_no_reg_and_mem_segment(self):

        parser = self.get_parser()

        trace_sample = r"""Time    Cycle   PC  Instr   Decoded instruction Register and memory contents
    905ns              86 00000e36 00a005b3 c.add            x11,  x0, x10       x11=00000e5c x10:00000e5c
    915ns              87 00000e38 00000693 c.addi           x13,  x0, 0         x13=00000000
    925ns              88 00000e3a 00000613 c.addi           x12,  x0, 0
    935ns              89 00000e3c 00000513 c.addi           x10,  x0, 0
    945ns              90 00000e3e 2b40006f c.jal             x0, 692
    975ns              93 000010f2 0d01a703 lw               x14, 208(x3)        x14=00002b20  x3:00003288  PA:00003358
    985ns              94 000010f6 00a00333 c.add             x6,  x0, x10        x6=00000000 x10:00000000
    995ns              95 000010f8 14872783 lw               x15, 328(x14)       x15=00000000 x14:00002b20  PA:00002c68
   1015ns              97 000010fc 00079563 c.bne            x15,  x0, 10        x15:00000000
"""
        csv_lines = parser.parse(trace_sample)

        expected_csv_lines = ['Time,Cycle,PC,Instr,Decoded instruction,Register and memory contents',
                              '905ns,86,00000e36,00a005b3,"c.add x11, x0, x10","x11=00000e5c, x10:00000e5c"',
                              '915ns,87,00000e38,00000693,"c.addi x13, x0, 0","x13=00000000"',
                              '925ns,88,00000e3a,00000613,"c.addi x12, x0, 0",""',
                              '935ns,89,00000e3c,00000513,"c.addi x10, x0, 0",""',
                              '945ns,90,00000e3e,2b40006f,"c.jal x0, 692",""',
                              '975ns,93,000010f2,0d01a703,"lw x14, 208(x3)","x14=00002b20, x3:00003288, PA:00003358"',
                              '985ns,94,000010f6,00a00333,"c.add x6, x0, x10","x6=00000000, x10:00000000"',
                              '995ns,95,000010f8,14872783,"lw x15, 328(x14)","x15=00000000, x14:00002b20, PA:00002c68"',
                              '1015ns,97,000010fc,00079563,"c.bne x15, x0, 10","x15:00000000"']

        self.assertEqual(csv_lines, expected_csv_lines)

    def test_no_operands_in_decoded_instruction_and_no_reg_and_mem(self):

        parser = self.get_parser()

        trace_sample = r"""Time    Cycle   PC  Instr   Decoded instruction Register and memory contents
    905ns              86 00000e36 00a005b3 c.add                   x11=00000e5c x10:00000e5c
    915ns              87 00000e38 00000693 c.addi                  x13=00000000
    925ns              88 00000e3a 00000613 c.addi
    935ns              89 00000e3c 00000513 c.addi           x10,  x0, 0
    945ns              90 00000e3e 2b40006f c.jal             x0, 692
    975ns              93 000010f2 0d01a703 lw               x14, 208(x3)        x14=00002b20  x3:00003288  PA:00003358
    985ns              94 000010f6 00a00333 c.add             x6,  x0, x10        x6=00000000 x10:00000000
    995ns              95 000010f8 14872783 lw               x15, 328(x14)       x15=00000000 x14:00002b20  PA:00002c68
   1015ns              97 000010fc 00079563 c.bne            x15,  x0, 10        x15:00000000
"""
        csv_lines = parser.parse(trace_sample)

        expected_csv_lines = ['Time,Cycle,PC,Instr,Decoded instruction,Register and memory contents',
                              '905ns,86,00000e36,00a005b3,"c.add","x11=00000e5c, x10:00000e5c"',
                              '915ns,87,00000e38,00000693,"c.addi","x13=00000000"',
                              '925ns,88,00000e3a,00000613,"c.addi",""',
                              '935ns,89,00000e3c,00000513,"c.addi x10, x0, 0",""',
                              '945ns,90,00000e3e,2b40006f,"c.jal x0, 692",""',
                              '975ns,93,000010f2,0d01a703,"lw x14, 208(x3)","x14=00002b20, x3:00003288, PA:00003358"',
                              '985ns,94,000010f6,00a00333,"c.add x6, x0, x10","x6=00000000, x10:00000000"',
                              '995ns,95,000010f8,14872783,"lw x15, 328(x14)","x15=00000000, x14:00002b20, PA:00002c68"',
                              '1015ns,97,000010fc,00079563,"c.bne x15, x0, 10","x15:00000000"']

        self.assertEqual(csv_lines, expected_csv_lines)

    def test_float_operands_in_decoded_instruction(self):

            parser = self.get_parser()

            trace_sample = r"""Time    Cycle   PC  Instr   Decoded instruction Register and memory contents
    6235ns             619 00000506 00032087 flw               f1, 0(x6)           f1=40800001  x6:0000290c  PA:0000290c
    6245ns             620 00000508 0815754b fnmsub.s         f10, f10,  f1,  f1  f10=4427827e f10:c326827d  f1:40800001  f1:40800001
    6255ns             621 0000050a 18107153 fdiv.s            f2,  f0,  f1        f2=3f800000  f0:40800001  f1:40800001
    6315ns             627 0000050e 18207153 fdiv.s            f2,  f0,  f2        f2=40800001  f0:40800001  f2:3f800000
    6495ns             645 00000512 e0011553 fclass.s         x10,  f2            x10=00000040  f2:40800001
    6505ns             646 00000516 202005d3 fsgnj.s          f11,  f0,  f2       f11=40800001  f0:40800001  f2:40800001
    6515ns             647 0000051a 20001653 fsgnjn.s         f12,  f0,  f0       f12=c0800001  f0:40800001  f0:40800001
    6525ns             648 0000051e 202026d3 fsgnjx.s         f13,  f0,  f2       f13=40800001  f0:40800001  f2:40800001
    6535ns             649 00000522 182071d3 fdiv.s            f3,  f0,  f2        f3=3f800000  f0:40800001  f2:40800001
    6595ns             655 00000526 e0019553 fclass.s         x10,  f3            x10=00000040  f3:3f800000
    6605ns             656 0000052a 1821f253 fdiv.s            f4,  f3,  f2        f4=3e7ffffe  f3:3f800000  f2:40800001
    6705ns             658 00000e8a fbdff06f c.jal             x0, -68      
    """
            csv_lines = parser.parse(trace_sample)

            expected_csv_lines = ['Time,Cycle,PC,Instr,Decoded instruction,Register and memory contents',
        '6235ns,619,00000506,00032087,"flw f1, 0(x6)","f1=40800001, x6:0000290c, PA:0000290c"', # 3 Mixed registers
        '6245ns,620,00000508,0815754b,"fnmsub.s f10, f10, f1, f1","f10=4427827e, f10:c326827d, f1:40800001, f1:40800001"', # 4 f registers
        '6255ns,621,0000050a,18107153,"fdiv.s f2, f0, f1","f2=3f800000, f0:40800001, f1:40800001"', # 3 f registers
        '6315ns,627,0000050e,18207153,"fdiv.s f2, f0, f2","f2=40800001, f0:40800001, f2:3f800000"',
        '6495ns,645,00000512,e0011553,"fclass.s x10, f2","x10=00000040, f2:40800001"', # 2 mixed registers
        '6505ns,646,00000516,202005d3,"fsgnj.s f11, f0, f2","f11=40800001, f0:40800001, f2:40800001"',
        '6515ns,647,0000051a,20001653,"fsgnjn.s f12, f0, f0","f12=c0800001, f0:40800001, f0:40800001"',
        '6525ns,648,0000051e,202026d3,"fsgnjx.s f13, f0, f2","f13=40800001, f0:40800001, f2:40800001"',
        '6535ns,649,00000522,182071d3,"fdiv.s f3, f0, f2","f3=3f800000, f0:40800001, f2:40800001"',
        '6595ns,655,00000526,e0019553,"fclass.s x10, f3","x10=00000040, f3:3f800000"',
        '6605ns,656,0000052a,1821f253,"fdiv.s f4, f3, f2","f4=3e7ffffe, f3:3f800000, f2:40800001"',
        '6705ns,658,00000e8a,fbdff06f,"c.jal x0, -68",""' # No register
    ]

            self.assertEqual(csv_lines, expected_csv_lines)
