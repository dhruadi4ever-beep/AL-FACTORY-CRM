package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class PlanningUiModel(
    val id: Int,
    val machineCode: String,
    val itemCode: String?,
    val employeeCode: String?,
    val state: String,
    val bobbinRequired: Boolean,
    val bobbinIssued: Boolean,
)

@Composable
fun ProductionPlanningScreen() {
    val plans = remember {
        listOf(
            PlanningUiModel(1, "M-001", "ITM-A", "E-010", "assigned", true, false),
            PlanningUiModel(2, "M-002", null, "E-011", "idle", false, false),
            PlanningUiModel(3, "M-003", "ITM-B", "E-012", "assigned", false, false),
        )
    }

    var machineCode by remember { mutableStateOf("M-001") }
    var itemCode by remember { mutableStateOf("ITM-A") }
    var employeeCode by remember { mutableStateOf("E-010") }
    var state by remember { mutableStateOf("assigned") }
    var bobbinRequired by remember { mutableStateOf(true) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Production Planning", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Plan machine, item, and operator assignments without recording actual production")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = machineCode, onValueChange = { machineCode = it }, label = { Text("Machine") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = itemCode, onValueChange = { itemCode = it }, label = { Text("Item") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = employeeCode, onValueChange = { employeeCode = it }, label = { Text("Employee") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = state, onValueChange = { state = it }, label = { Text("State") }, modifier = Modifier.fillMaxWidth())

                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Text(text = "Bobbins required")
                    Switch(checked = bobbinRequired, onCheckedChange = { bobbinRequired = it })
                }
            }
        }

        Text(text = "Current plan", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(plans) { plan ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(text = "${plan.machineCode} • ${plan.state}", style = MaterialTheme.typography.titleSmall)
                        Text(text = "Item: ${plan.itemCode ?: "Not assigned"}")
                        Text(text = "Employee: ${plan.employeeCode ?: "Not assigned"}")
                        Text(text = "Bobbins required: ${if (plan.bobbinRequired) "Yes" else "No"} | Bobbins issued: ${if (plan.bobbinIssued) "Yes" else "No"}")
                    }
                }
            }
        }
    }
}
