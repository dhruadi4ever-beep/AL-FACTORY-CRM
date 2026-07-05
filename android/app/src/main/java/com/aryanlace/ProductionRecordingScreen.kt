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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class ProductionEntryUiModel(
    val id: Int,
    val machineCode: String,
    val itemCode: String,
    val bunches: String,
    val status: String,
)

@Composable
fun ProductionRecordingScreen() {
    val entries = remember {
        listOf(
            ProductionEntryUiModel(1, "M-001", "ITM-A", "10", "available"),
            ProductionEntryUiModel(2, "M-002", "ITM-A", "15", "partially_assigned"),
        )
    }

    var machineCode by remember { mutableStateOf("M-001") }
    var itemCode by remember { mutableStateOf("ITM-A") }
    var bunches by remember { mutableStateOf("10") }
    var status by remember { mutableStateOf("available") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Actual Production Recording", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Record actual production per machine and update produced inventory")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = machineCode, onValueChange = { machineCode = it }, label = { Text("Machine") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = itemCode, onValueChange = { itemCode = it }, label = { Text("Item") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = bunches, onValueChange = { bunches = it }, label = { Text("Bunches") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = status, onValueChange = { status = it }, label = { Text("Status") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Production history", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(entries) { entry ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Text(text = entry.machineCode, style = MaterialTheme.typography.titleSmall)
                            Text(text = entry.status)
                        }
                        Text(text = "Item: ${entry.itemCode}")
                        Text(text = "Bunches: ${entry.bunches}")
                    }
                }
            }
        }
    }
}
