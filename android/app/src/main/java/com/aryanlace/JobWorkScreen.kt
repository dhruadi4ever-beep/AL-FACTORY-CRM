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

private data class JobWorkUiModel(
    val id: Int,
    val workerCode: String,
    val itemCode: String,
    val assignedBunches: String,
    val status: String,
)

@Composable
fun JobWorkScreen() {
    val assignments = remember {
        listOf(
            JobWorkUiModel(1, "JW-001", "ITM-A", "25", "in_progress"),
            JobWorkUiModel(2, "JW-002", "ITM-B", "10", "completed"),
        )
    }

    var workerCode by remember { mutableStateOf("JW-001") }
    var itemCode by remember { mutableStateOf("ITM-A") }
    var assignedBunches by remember { mutableStateOf("25") }
    var status by remember { mutableStateOf("in_progress") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Job Work Assignment", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Assign whole bunches to job workers and track partial completion")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = workerCode, onValueChange = { workerCode = it }, label = { Text("Job worker") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = itemCode, onValueChange = { itemCode = it }, label = { Text("Item") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = assignedBunches, onValueChange = { assignedBunches = it }, label = { Text("Assigned bunches") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = status, onValueChange = { status = it }, label = { Text("Status") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Assignments", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(assignments) { assignment ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Text(text = assignment.workerCode, style = MaterialTheme.typography.titleSmall)
                            Text(text = assignment.status)
                        }
                        Text(text = "Item: ${assignment.itemCode}")
                        Text(text = "Assigned bunches: ${assignment.assignedBunches}")
                    }
                }
            }
        }
    }
}
